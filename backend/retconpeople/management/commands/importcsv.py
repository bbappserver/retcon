import imp
from django.core.management.base import BaseCommand, CommandError
from retconpeople.models import *
from retconcreatives.models import *
from django.conf.locale import LANG_INFO
from django.db import transaction
from django.db.models import QuerySet,Model
import pandas as pd


class ImportAction:
    
    model : Model = None
    selectors={}
    
    def required_create_fields(self):
        return [f for f in self.model._meta.get_fields() if not getattr(f, 'blank', False) is True]
    
    def do_fields_mismatch(self):
        '''Returns true if using the same id, but the imported data mismatches the data on file'''
        raise NotImplementedError()
    def resolve_field_mismatch(self):
        '''Interactive prompts to resolve a filed mismatch'''
        raise NotImplementedError()
    
    def get_by_string(self,s) -> QuerySet:
        return self.model.filter_by_fuzzy_string(s)
    
    def print_for_disambiguation(self,obj):
        '''Prints enough infomation on the target object for it to be  distinguished from another'''
    
    def resolve_ambiguous_selection(self):
        raise NotImplementedError()
    
    def confirm_selection(self):
        raise NotImplementedError()
    
    def search_string_fuzzy_match(self,a,b):
        '''Returns true if strings a and b likely refer to the same item or are identical'''
        raise NotImplementedError()
    
    def search_by_selectors(self,d:dict) -> QuerySet:
        '''Produces a list of candidates given the dictionary of lookup keys, possible one or empty'''
        qs=self.model.objects.none()
        for f in self.selectors.items():
            if f.key in self.selectors:
                qs=qs.union(f(d))
        return qs
    
    def interactive_create(self,d:dict,defaulted_fields={}):
        raise NotImplementedError()
    
    def suggest_creation_assignment(self,d:dict):
        raise NotImplementedError()
    
class GetOrCreatePersonImportAction(ImportAction):
    model=Person
    selectors={
        ('Person.fuzzy_string_lookup',):'get_by_string',
        ('Person.first_name','Person.last_name'):'get_by_name',
        ('Person.pseudonym',):'get_by_pseudonym',
        ('Person.url',):'get_by_url'
    }
    yields=('Person')
    pass

class GetOrCreateCompanyImportAction(ImportAction):
    model=Company
    selectors={
        ('Company.fuzzy_string_lookup',):'get_by_string',
    }
    yields=('Company',)
    pass

class GetOrCreateSeriesImportAction(ImportAction):
    model=Series
    selectors={
        ('Company','Series.name','Series.release_date__year'):'get_by_company_name_year',
        ('Company','Series.name'):'get_by_company_name',
        ('Series.name',):'get_by_name'
    }

class GetOrCreateEpisodeImportAction(ImportAction):
    model=Episode
    selectors={
        ('Episode.part_of','Episode.order_in_series','Episode.name'):'get_by_series_ordinal_and_name',
        ('Episode.part_of','Episode.order_in_series'):'get_by_series_and_ordinal',
        ('Episode.produced_by','Episode.name'):'get_by_company_and_name'
    }
    yields=('Episode')
    pass

class GetOrCreateRoleImportAction(ImportAction):
    model=Character
    selectors={
        ('Character.name',):'get_by_string'
    }
    yields=('Character')
    pass

class GetOrCreateContentUrlAction(ImportAction):
    selectors={
    ('ContentURL.url',):'get_by_string'
    }
    yields=('remotables.ContentUrl')
    pass

class UpdatePersonAction:
    pass

class UpdateEpisodeAction:
    pass

class AssociateImportAction:
    
    @property
    def is_many_to_many(self):
        raise NotImplementedError()
    
    def related_manager_field_name(self):
        raise NotImplementedError()
    
    def reverse_accessor_field_name(self):
        raise NotImplementedError()
    
    def intermediate_table(self):
        raise NotImplementedError()
    
    def old_value(self):
        raise NotImplementedError()
    
    def new_value(self):
        raise NotImplementedError()
    
    def run(self):
        raise NotImplementedError()

class AssociateEpsiodeToCompanyImportAction(AssociateImportAction):
    requires=['Episode','Company']
    
    @property
    def is_many_to_many(self): return True

class AssociateEpsiodeToSeriesImportAction(AssociateImportAction):
    requires=["Episode","Series"]

class AssociatePersonPortraylEpisodeImportAction(AssociateImportAction):
    model: Model=Portrayal
    yields=['Portrayl']
    requires=['Episode','Person','Role']


get_or_create_actions=[    
    GetOrCreateCompanyImportAction,
    GetOrCreateSeriesImportAction,
    GetOrCreateEpisodeImportAction,
    GetOrCreatePersonImportAction,
    GetOrCreateRoleImportAction
]    

associate_actions=[
    AssociateEpsiodeToCompanyImportAction,
    AssociateEpsiodeToSeriesImportAction,
    AssociatePersonPortraylEpisodeImportAction
]
recommended_action_order=[
    GetOrCreateCompanyImportAction,
    GetOrCreateSeriesImportAction,
    GetOrCreateEpisodeImportAction,
    UpdateEpisodeAction,
    AssociateEpsiodeToCompanyImportAction,
    AssociateEpsiodeToSeriesImportAction,
    GetOrCreatePersonImportAction,
    UpdatePersonAction,
    GetOrCreateRoleImportAction,
    AssociatePersonPortraylEpisodeImportAction
]

from enum import IntEnum
class ForeignFieldUpdateAction(IntEnum):
    
    LEAVE_AS_IS=-1
    LEAVE_AS_IS_OR_SET_IF_NULL=0
    REPLACE=1
    ALWAYS_ASK=2

class ManyToManyFieldUpdateAction(IntEnum):
    ADD=0
    REPLACE=1
    ALWAYS_ASK=2

class MappedRow:
    pass
class ResolvedRow:
    pass

class Command(BaseCommand):
    help = 'Checks to see if resources for named users are dead (HTTP 404)'
    def add_arguments(self, parser):
        prxhelp="Import objects from a table"
        parser.add_argument('file', nargs='?', type=str,default='dat.csv')
        # parser.add_argument('proxy_domain_format_string', nargs='?', type=str,help=prxhelp)
        # parser.add_argument('--head', action='store_true',help='use head instead of get. can save on bandwidth, but unsupported by some servers')
        # parser.add_argument('-y', action='store_true',help='Assume yes to all prompts')

    def prompt_select_column(self):
        
        i=0
        for x in self.keyMap.items():
            print(f"{i}){x[0]}:{x[1]}")
            i+=1
        return input()
    
    def handle(self, *args, **options):
        
        self._keys={
            'Person name':[Person,'Person.fuzzy_string_lookup'],
            'Person first name':[Person,'Person.first_name'],
            'Person last name':[Person,'Person.last_name'],
            'Person pseudonym':[Person,'Person.pseudonym__fuzzy'],
            'Character Name / Portrayl Role Name':[Character,'Role.name'],
            'Company/Studio name':[Company,'Company.name'],
            'Episode name':[Episode,'Episode.name'],
            'Episode number':[Episode,'Episode.order_in_series'],
            'Episode publication date':[Episode,'Episode.published_on'],
            'Series Name':[Series,'Series.name'],
            'Series URL':[Series,'Series.url']
        }
        
        #Map fields to from csv to defined key names
        dat=[]
        csv=[]
        included_fields=[]
        for x in csv:
            r=MappedRow()
            dat.append(r)
            r._r=ResolvedRow()
            
            for f in included_fields:
                v=x[f.column_name]
                setattr(f.field,v)
        
        #Create or retreive all entities
        #Construct a replacement table
        #This way we can cache already resolved entities and only ask about the remaining fields we encounter.
        #[publisher: Company, series: Series, episode : Episode, actor : Person, role : Character]
        
        #Begin Transaction
        #1.For each global field, resolve field to entity, a global field is one for which there is no column
        g_publisher = g_episode = g_series=g_actor=g_role=None
        # Usually this is either the company or the actor depending how the data was scraped
        # If entity not exists, then create
        # E.g. [publisher=Disney, series="Lilo and Stitch"]
        
        #1B. Figure out if we are attaching episodes to companies, people to episodes or both
        
        #2 For each non-global field try to resolve to existing entity
        # Offer to replace like equivalent strings
        
        N=len(dat) # N is the count of rows
        for i in range(N):
            row_in=dat[i]
            
            pu=row_in.publisher_url
            au=row_in.actor_url
            eu=row_in.episode_url
            su=row_in.actor_url
            
            row_in.publisher = Company.get_by_url(pu)
            row_in.episode = Episode.get_by_url(eu)
            row_in.series = Series.get_by_url(su)
            row_in.actor = Person.get_by_url(au)
            #row_out.role
        #2.0 If we have resolvable urls try to autoreplace all of those first
        
        #3.0 fuzzy resolve remainder
        for i in range(N):
            row=dat[i]
            # 3.1 If has companies
            # If publisher is not global get Company with name
            v="Disney" #TODO get from mapping
            
            if Company in included_fields and g_publisher is None and row.publisher is None:
                c_publishers= Company.find_by_fuzzy_name(v)
            # If not exists Create
            
            # 3.2 If has series
            # If series is not global get series with name
            if Series in included_fields and g_series is None and row.series is None:
                raise NotImplementedError()
            # Series with url
            # Series with publisher
            # If not exists Create, associate urls
            
            # 3.3 If has episodes
            if Episode in included_fields and g_episode is None and row.episode is None:
                raise NotImplementedError()
                # Episode with name and publisher and series, if empty or next then
                # Episode with name and series, if empty or next then,
                # Episode with name and publisher, if no candidate
                # Episode with name if no candidate
                
                # Create episode with series and publisher and associate urls
            
            #3.4 If has people
            
            if Person in included_fields and g_actor is None and row.actor is None:
                raise NotImplementedError()
                #If there are episodes and role not global resolve to characters
                
                #If person not null
                #Find person in role attached to episode
                #Find person in any role attached to episode
                #Find person by attributes
                # Offer to create if no candidate
                # Associate urls
                # Create portrayl(person,role,episode)
        
        self.selector_to_table_field={}
        
        self.keyMap = {x:None for x in self._keys.keys()}
        df=None
        with open(options['file']) as f:
            df= pd.read_csv(f)
            print(df)
        
        publisher=list(Company.objects.filter(name='Legend Men'))[0]
        role=list(Character.objects.filter(name='self'))[0]
        for x in df['list-item']:
            
            with transaction.atomic():
                performer_name=x
                episode_name=x
                episode=None
                
                if '&' in performer_name or ' and ' in performer_name:
                    print("WARN:Skip performer creation looksl ike key describes multiple")
                else:
                    candidates= list(Person.get_by_pseudonym(performer_name))
                    print(candidates)
                    if len(candidates)<2:
                        if len(candidates)<1:
                            performer=Person()
                            performer.save()
                            performer.add_pseudonym(performer_name)
                        else:
                            performer = candidates[0]
                    else:
                        raise NotImplementedError()
                    
                    try:
                        for e in Episode.objects.filter(name=episode_name):
                            if publisher in e.published_by.all():
                                episode = e
                                break
                            else:
                                episode = e
                        if episode is None:
                            episode = Episode(name=episode_name,medium=Episode.MOVIE)
                            episode.save()
                            
                            if performer:
                                episode.add_portrayl(role,performer)
                            episode.published_by.add(publisher)
                        else:
                            if episode.portrayal_set.filter(actor_id=performer.id):
                                episode.published_by.add(publisher)
                            
                    except Episode.DoesNotExist:
                        pass

            
            
        
        self.column_keys=df.keys()
        
        self.collect_selectors()
        self.prompt_selector_to_table_field()
        
        for a in get_or_create_actions:
            l=[]
            for r in df.axes:
                ids=a.run(r)
                l.append(id)
            
            news = pd.Series(l)
        
        #we now have a table with columns that are ether length 1 because of creation or unabiguous retrival or more than one because of ambiguity
        #first we will disambiguate which fields these should apply to, that way if we find the field is already set to that we can skip asking the user
        
        #confirm which fields should be attached to which generated objects (e.g. if generating company, then 
        # do we do Episode.published_by, or Series.published_by or both
        self.disambiguate_association()
        
        
        #update_direct_fields_and_associations
        #Now do updating, check if the fields of the retrieved objects match the fields selected from the table
        #prompt to overwrite or keep.  This works fine for direct fields an foreign keys
        
    
        
    
    def collect_selectors(self):
        self.selectors=set()
        for x in get_or_create_actions:
            for y in x.selectors:
                for z in y:
                    if z not in self.selectors:
                        self.selectors.add(z)
        self.selectors=sorted(self.selectors)
    
    def prompt_selector_to_table_field(self):
        pass
        self.selector_to_table_field['list-item']='Person.pseudonym'
    
        
        #raise NotImplementedError()
       
    def disambiguate_association(self):
        self.field_set_action={x:ForeignFieldUpdateAction.LEAVE_AS_IS for x in self.selectors}
        print(self.field_set_action)
        
    def get_types_of_object_to_fetched_or_create():
        raise NotImplementedError()
    
    def confirm_actions(self):
        
        for a in recommended_action_order:
            missing_required=set(a.requires)-self.provided_fields
            if missing_required:
                print(f"Action {a} will be skipped because one or more fields have not been provided")
                print(missing_required)
                print("1)Provide defaults for missing fields")
                print("2)Skip")
        
        
    
    



        




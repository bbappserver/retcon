function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function checkContents()
{
    var name= "test";
    return $.get('GET','/API/strings?name='+name, function(data)
    {
        if (data.status==404)
        {
            setNeedsCreate($this);
        }
        else if (data.status==200)
        {
            setExists($this);
        }
    });
}

function createStringObject(s)
{
    var params={"name":s;}
    return $.post('/API/strings',params);
}

$('.sharedstringfield').keyup(function( event ) {
    $this.checkContents();
});
$( ".sharedstringfield" ).submit(function( event ) {
    alert( "Handler for .submit() called." );
    if(needsCreate)
    {
        $this.value=createStringObject($thid.value)
    }
    event.preventDefault();
  });
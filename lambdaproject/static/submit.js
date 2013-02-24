$(document).ready(function() {
  var now = new Date();
  var formatted = now.format("dd.mm.yyyy");
  $('#id_date').val(formatted);
  $('#progress-indicator').hide();
  var bar = $('.bar');
  var percent = $('.percent');

  $('#videoForm').ajaxForm({
    beforeSend: function(xhr, abort) {
        var errorFields = [];
        if (window.videoForm.title.value == '')
        {
            errorFields.push('title');
        }

        if (!window.videoForm.channel.value)
        {
            errorFields.push('channel');
        }

        if (!window.videoForm.kind.value)
        {
            errorFields.push('kind');
        }

        if (!window.videoForm.originalFile.value)
        {
            errorFields.push('file');
        }

        if (errorFields.length > 0)
        {
            alert('An error occured on the following fields:\n' + errorFields.join(', ') + '\nPlease validate your input.')
            xhr.abort();
        }

        var percentVal = '0%';
        bar.width(percentVal)
        percent.html(percentVal);
    },
    uploadProgress: function(event, position, total, percentComplete) {
        var percentVal = percentComplete + '%';
        bar.width(percentVal)
        percent.html(percentVal);
        document.title = 'OwnTube - Hochladen - ' + percentVal;
    },
        complete: function(xhr) {
                if (xhr.status == 200){
                        alert("Danke, ihr Video wird trancodiert und sollte bald zur Verfügung stehen");
                        window.location.href = "/status/";
                }else {
                        alert("Tut uns leid, das hat nicht geklappt, bitte noch mal versuchen oder den Admin nerven");
                }
        }
  });
});

$(document).ready(function() {
	var now = new Date();
	var formatted = now.format("dd.mm.yyyy");
	$('#id_date').val(formatted);
	$('#progress-indicator').hide();
	var bar = $('.bar');
	var percent = $('.percent');

	$('#videoForm').ajaxForm({
		beforeSend: function(xhr) {
			var validator = $("#videoForm").validate({errorClass: "text-error",})
			if (!validator.form()) {
				$("#formError").show();
				xhr.abort();
			} else {
				$("#formError").hide();
				$('#progress-indicator').show();
			}
			var percentVal = '0%';
			bar.width(percentVal)
			percent.html(percentVal);
		},
		uploadProgress: function(event, position, total, percentComplete) {
			var percentVal = percentComplete + '%';
			bar.width(percentVal)
			percent.html(percentVal);
			document.title = 'LambdaCast - Hochladen - ' + percentVal;
		},
		complete: function(xhr) {
			if (xhr.status == 200){
				// TODO: remove alert
				alert("Danke, ihr Video wird trancodiert und sollte bald zur Verfügung stehen");
				window.location.href = "/status/";
			}else {
				$("#formError").html("Tut uns leid, das hat nicht geklappt, bitte noch mal versuchen oder den Admin nerven.");
				$("#formError").show();
			}
		}
	});
});

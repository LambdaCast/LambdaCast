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
			document.title = 'Upload - ' + percentVal;
		},
		complete: function(xhr) {
			if (xhr.status == 200){
				// TODO: remove alert
				alert("Thank you, your media will be transcoded and should be available soon.");
				window.location.href = "/status/";
			}else {
				$("#formError").html("An error accured. Please, try again or contact the administrator.");
				$("#formError").show();
			}
		}
	});
});

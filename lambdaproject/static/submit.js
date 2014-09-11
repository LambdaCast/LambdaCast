$(document).ready(function() {
	$('#progress-indicator').hide();
	$('#upload-success').hide();
	$('#form-error').hide();
	var bar = $('#bar');
	var percent = $('.percent');

	$('#mediaitemForm').ajaxForm({
		beforeSend: function(xhr) {
			var validator = $("#mediaitemForm").validate({errorClass: "text-error",});
			if (!validator.form()) {
				$("#form-error").show();
				xhr.abort();
			} else {
				$("#form-error").hide();
				$('#progress-indicator').show();
			}
			var percentVal = '0%';
			bar.attr('aria-valuenow', percentVal)
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
				$('#upload-success').show();
			}else {
				$("#form-error").show();
			}
		}
	});
});

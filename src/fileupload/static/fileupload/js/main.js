$(function () {
    // Initialize the jQuery File Upload widget:
    $('#fileupload').fileupload({
        url: '.',
        acceptFileTypes: /(\.|\/)(gif|jpe?g|png|tiff?)$/i,
        paramName: 'files',
        showElementClass: 'show',
        limitConcurrentUploads: 3,

        messages: {
            unknownError: 'Nieznany błąd',
            uploadedBytes: "Przesłane dane przekraczają rozmiar pliku",
            maxNumberOfFiles: "Zbyt wiele plików",
            acceptFileTypes: "Niedozwolony typ pliku",
            maxFileSize: "Plik jest zbyt duży",
            minFileSize: "Plik jest zbyt mały",
            error: "Błąd",
            start: "Start",
            cancel: "Anuluj",
            delete: "Usuń",
            processing: "Przetwarzanie…",
        },
    });

    // Load existing files:
    $('#fileupload').addClass('fileupload-processing');
    $.ajax({
      url: $('#fileupload').fileupload('option', 'url'),
      dataType: 'json',
      context: $('#fileupload')[0]
    })
      .always(function () {
        $(this).removeClass('fileupload-processing');
      })
      .done(function (result) {
        $(this)
          .fileupload('option', 'done')
          .call(this, $.Event('done'), { result: result });
      });

});

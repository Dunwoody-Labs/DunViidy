Dropzone.options.myDropzone = {
    paramName: "file",
    maxFilesize: 10, // MB
    acceptedFiles: ".jpg,.png,.pdf,.mp4",
    init: function () {
        this.on("success", function (file, response) {
            console.log("File uploaded successfully");
        });
    }
};

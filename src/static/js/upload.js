function formchagne() {
    var sel = document.getElementsByName("type")[0].value;
    if (sel == 'ios') {
        document.getElementById("package_name").required = false;
        document.getElementById("bundle_id").required = true;
        document.getElementById("package_name_label").style.display = "none";
        document.getElementById("bundle_id_label").style.display = "";
        document.getElementById("file").accept = ".ipa";
        document.getElementById("file").value = "";
        document.getElementById("md5").value = "";
        document.getElementById("package_name").value = "";
    }

    if (sel == 'android') {
        document.getElementById("package_name").required = true;
        document.getElementById("bundle_id").required = false;
        document.getElementById("package_name_label").style.display = "";
        document.getElementById("bundle_id_label").style.display = "none";
        document.getElementById("file").accept = ".apk";
        document.getElementById("file").value = "";
        document.getElementById("md5").value = "";
        document.getElementById("bundle_id").value = "";
    }
}

document.getElementById('file').addEventListener('change', function () {
    var blobSlice = File.prototype.slice || File.prototype.mozSlice || File.prototype.webkitSlice,
        file = this.files[0],
        chunkSize = 2097152,
        chunks = Math.ceil(file.size / chunkSize),
        currentChunk = 0,
        spark = new SparkMD5.ArrayBuffer(),
        fileReader = new FileReader();

    fileReader.onload = function (e) {
        spark.append(e.target.result);
        currentChunk++;

        if (currentChunk < chunks) {
            loadNext();
        } else {
            var app_md5 = document.getElementById('md5');
            app_md5.value = spark.end();
        }
    };

    fileReader.onerror = function () {
        console.warn('oops, something went wrong.');
    };

    function loadNext() {
        var start = currentChunk * chunkSize,
            end = ((start + chunkSize) >= file.size) ? file.size : start + chunkSize;

        fileReader.readAsArrayBuffer(blobSlice.call(file, start, end));
    }

    loadNext();
});

function iconCheck(target){
    var fileSize = 0;
    fileSize = target.files[0].size;
    var size = fileSize / 1024;
    if(size>1000){
        alert("图标不能大于1M");
        target.value="";
        document.getElementById("icon_label").style.display = "none";
        return false;
    }
}

$("#icon").on("change", function () {
    var files = !!this.files ? this.files : [];
    if (!files.length || !window.FileReader) return;
    if (/^image/.test(files[0].type)) {
        var reader = new FileReader();
        reader.readAsDataURL(files[0]);
        reader.onloadend = function () {
            $("#preview_img").css("background-image", "url(" + this.result + ")");
            document.getElementById("icon_label").style.display = "";   
        }
    }
});

document.getElementById("icon").addEventListener("change",function () {
    document.getElementById("icon_label").style.display = "none";
});

document.getElementById('upload_form').reset()

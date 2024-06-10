// ======= KNOWLEDGE BASE PAGE LOGIC ==========
var Grid = gridjs.Grid;
var html = gridjs.html;
const API_URI = 'localhost:8080';

var lastFilesChecksum = '';

var downloadFileWithId = function(id) {
    // download file with id
    console.info('Downloading file with id: ' + id)
}
var deleteFileWithId = function(id) {
    // delete file with id
    console.info('Deleting file with id: ' + id)
}

var formatStatus = function(cell) {
    // if cell == 'Synced' return '<div class="synced">Synced</div>'
    // if cell == 'Syncing' return '<div class="syncing">Syncing</div>'
    // if cell == 'Not Synced' return '<div class="not-synced">New</div>'
    if (cell == 'indexed') {
        return html('<div class="d-flex justify-content-left"><div class="pr-2 text-success no-select">Indexed</div> <span class="checkmark"><div class="checkmark_stem"></div><div class="checkmark_kick"></div></span> </div>');
    } else if (cell == 'processing') {
        return html('<div class="d-flex justify-content-left"><div class="pr-2 text-info no-select">Processing</div><div class="loader"></div> </div>');
    } else if (cell == 'deleting') {
        return html('<div class="d-flex justify-content-left"><div class="pr-2 text-danger no-select">Deleting</div> <div class="loader-red"></div> </div>');
    }
}

var formatActions = function(_, row) {
    var canDelete = false;
    var canDownload = false;
    if (row.cells[1].data == 'indexed') {
        canDelete = true;
        canDownload = true;
    } else if (row.cells[1].data == 'processing') {
        canDelete = false;
        canDownload = false;
    } else if (row.cells[1].data == 'deleting') {
        canDelete = false;
        canDownload = false;
    }
    html_str = ""
    if (canDownload) {
        html_str += `<div class="btn btn-info m-1" onclick="downloadFileWithId('${row.cells[0].data}')">Download</div>`;
    } 
    if (canDelete) {
        html_str += `<div class="btn btn-danger m-1" onclick="deleteFileWithId('${row.cells[0].data}')">Delete</div>`;
    }
    if (canDelete == false && canDownload == false) {
        return html('<div class="m-2 text-muted no-select">N/A</div>');
    }
    console.log(html_str);
    return html(`<div class="d-flex justify-content-left">${html_str}</div>`);
}

const mygrid = new Grid(
    { 
        columns: [
            'File Name', 
            { 
                name: 'Status',
                formatter: formatStatus
            }, 
            {
                name: 'Actions',
                formatter: formatActions
            }
        ],
        sort: true,

        data: [
        ]
    },
).render(document.getElementById('table'));

// ======= FETCH FILES ==========

var fetchFiles = async function() {
    // Fetch files from the server
    url = `http://${API_URI}/api/files`;
    let response = await fetch(url);
    let data = await response.json();
    if (response.status != 200) {
        showFailureAlert('Failed to fetch files');
        return;
    }
    // Calculate checksum
    let files_checksum = await checksum(JSON.stringify(data));
    if (files_checksum == lastFilesChecksum) {
        return;
    }
    else {
        console.info('Files checksum changed, updating UI')
        lastFilesChecksum = files_checksum;
        let files = data;
        let files_data = [];
        for (var i = 0; i < files.length; i++) {
            let file = files[i];
            let file_data = [file.filename, file.status, ''];
            files_data.push(file_data);
        }
        mygrid.updateConfig({data: files_data});
        mygrid.forceRender();
    }
}

// ======= FILES DROPZONE ==========
var files_in_queue = {};
var upload_in_progress = false;
const ACCPETED_FILE_TYPES = ['application/pdf', 'text/plain'];
// Get the dropzone element
var dropzone = document.querySelector('.dropzone');

var delete_file = function(file_id) {
    // Delete file from the queue
    delete files_in_queue[file_id];
    updateFileUI();
}

var uploadFile = async function(file) {
    let extension = file.name.split('.').pop();
    let filename_no_extension = file.name.replace(/\.[^/.]+$/, "");
    let normalizedFileName = filename_no_extension.replace(/[^a-zA-Z0-9]/g, '_');
    let formData = new FormData();
    formData.append('file', file, normalizedFileName+'.'+extension);
    url = `http://${API_URI}/api/files/upload`;
    let response = await fetch(url, {
        method: 'POST',
        mode: 'no-cors', // no-cors mode to avoid CORS issues
        body: formData
    });
    let data = await response.json();
    if (response.status == 409) {
        showFailureAlert('File with the same name already exists');
        return 1;
    }
    else if (response.status != 200) {
        showFailureAlert('Failed to upload file');
        return 1;
    }
    return 0;
}

var uploadFilesToServer = async function(files) {
    // Upload files to the server
    var statusAccum = 0;
    for (var i = 0; i < files.length; i++) {
        var file = files[i];
        console.log('Uploading file: ' + file.name);
        document.getElementById('uploading-files-progress-show').innerHTML = 'Uploading Files (' + (i + 1) + '/' + files.length + ')';
        statusAccum += await uploadFile(file);
        
    }
    if (statusAccum == 0) {
        showSuccessAlert('Files uploaded successfully');
    }
    document.getElementById('uploading-files').hidden = true;
    upload_in_progress = false;
    fetchFiles();
}

var updateFileUI = function() {
    // Remove all files from the UI
    document.querySelector('.dropzone-files').innerHTML = '';
    for (var key in files_in_queue) {
        console.log('Key: ' + key + ' Value: ' + files_in_queue[key].name);
        var file_element = document.createElement('div');
        file_element.classList.add('p-2', 'file');
        file_element.id = key;
        file_element.onclick = function() {
            delete_file(this.id);
        }
        file_element.innerHTML = files_in_queue[key].name;
        document.querySelector('.dropzone-files').appendChild(file_element);
    }

    if (Object.keys(files_in_queue).length == 0) {
        document.getElementById('has-files').hidden = true;
    }
    if (Object.keys(files_in_queue).length > 0) {
        document.getElementById('has-files').hidden = false;
    }
}

var uploadKB = function() {
    // Lock the upload button
    upload_in_progress = true;
    // Upload files in the queue
    console.log('Uploading files in the queue');
    const files_in_queue_copy = Object.values(files_in_queue);
    files_in_queue = {};
    updateFileUI();
    document.getElementById('uploading-files').hidden = false;
    document.getElementById('uploading-files-progress-show').innerHTML = 'Uploading Files (0/' + files_in_queue_copy.length + ')';
    console.log(files_in_queue_copy);
    uploadFilesToServer(files_in_queue_copy)
    
}

var addFile = function(file) {
    // Add file to the queue
    var random_id = Math.floor(Math.random() * 1000000);
    files_in_queue[random_id] = file;
    updateFileUI();
}

// Add event listener for the 'dragover' event
dropzone.addEventListener('dragover', function(event) {
    // Prevent default behavior (Prevent file from being opened)
    event.preventDefault();
});

// Add event listener for the 'drop' event
dropzone.addEventListener('drop', function(event) {
    // Prevent default behavior (Prevent file from being opened)
    event.preventDefault();
    if (upload_in_progress) {
        showFailureAlert('Please wait for the current upload to finish');
        return;
    }

    // Use DataTransfer.files property to access file(s)
    if (event.dataTransfer.items) {
        // Use DataTransferItemList interface to access the file(s)
        for (var i = 0; i < event.dataTransfer.items.length; i++) {
            // If dropped items aren't files, reject them
            if (event.dataTransfer.items[i].kind === 'file') {
                // Check file type
                var file_type = event.dataTransfer.items[i].type;
                console.log('File[' + i + '].type = ' + file_type);
                if (ACCPETED_FILE_TYPES.includes(file_type) == false) {
                    showFailureAlert('We only accept PDF and Text files');
                    continue;
                }

                var file = event.dataTransfer.items[i].getAsFile();
                console.log('File[' + i + '].name = ' + file.name);
                addFile(file);
            }
        }
    } else {
        // Use DataTransfer interface to access the file(s)
        for (var i = 0; i < event.dataTransfer.files.length; i++) {
            console.log('File[' + i + '].name = ' + event.dataTransfer.files[i].name);
        }  
    }
});

// On document ready
document.addEventListener('DOMContentLoaded', function() {
    fetchFiles();
    // Every 60 seconds fetch files
    setInterval(fetchFiles, 5000); // 60000 milliseconds = 60 seconds
});

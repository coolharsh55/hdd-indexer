// PAGE LOAD
$(document).ready(function() {
    $.get( "/crawler/", {'status': true,}, function(data) {
        if (data['status'] === true) {
            $('#crawler-status').text('RUNNING');
            $('#crawler-status').removeClass('label-danger').addClass('label-success');
            $('#crawler-switch').text('Stop Crawler');
            $('#crawler-switch').removeClass('btn-success').addClass('btn-danger');
            $('#crawler-status-info').addClass('fa-spin');
            $('#crawler-status-info').show();
            $('#crawler-crawl-status').show();
            $('#crawler-files-evaluated').text(data['files_evaluated']);
            $('#crawler-movies-found').text(data['movies_found']);
            $('#crawler-movies-added').text(data['movies_added']);
        } else {
            $('#crawler-status').text('STOPPED');
            $('#crawler-status').removeClass('label-success').addClass('label-danger');
            $('#crawler-switch').text('Start Crawler');
            $('#crawler-switch').removeClass('btn-danger').addClass('btn-success');
            $('#crawler-status-info').removeClass('fa-spin');
            $('#crawler-status-info').hide();
            $('#crawler-crawl-status').hide();
        }
    });
    $.get( "/loader/", {'status': true,}, function(data) {
        if (data['status'] === true) {
            $('#loader-status').text('RUNNING');
            $('#loader-status').removeClass('label-danger').addClass('label-success');
            $('#loader-switch').text('Stop Organizer');
            $('#loader-switch').removeClass('btn-success').addClass('btn-danger');
            $('#loader-status-info').addClass('fa-spin');
            $('#loader-status-info').show();
            $('#loader-load-status').show();
            $('#loader-movies-evaluated').text(data['movies_evaluated']);
            $('#loader-metadata-downloaded').text(data['metadata_downloaded']);
            $('#loader-movies-skipped').text(data['movies_skipped']);
        } else {
            $('#loader-status').text('STOPPED');
            $('#loader-status').removeClass('label-success').addClass('label-danger');
            $('#loader-switch').text('Start Loader');
            $('#loader-switch').removeClass('btn-danger').addClass('btn-success');
            $('#loader-status-info').removeClass('fa-spin');
            $('#loader-status-info').hide();
            $('#loader-load-status').hide();
        }
    });
    $.get( "/organizer/", {'status': true,}, function(data) {
        if (data['status'] === true) {
            $('#organizer-status').text('RUNNING');
            $('#organizer-status').removeClass('label-danger').addClass('label-success');
            $('#organizer-switch').text('Stop Organizer');
            $('#organizer-switch').removeClass('btn-success').addClass('btn-danger');
            $('#organizer-status-info').addClass('fa-spin');
            $('#organizer-status-info').show();
            $('#organizer-loade-status').show();
            $('#organizer-files-evaluated').text(data['files_evaluated']);
        } else {
            $('#organizer-status').text('STOPPED');
            $('#organizer-status').removeClass('label-success').addClass('label-danger');
            $('#organizer-switch').text('Start Organizer');
            $('#organizer-switch').removeClass('btn-danger').addClass('btn-success');
            $('#organizer-status-info').removeClass('fa-spin');
            $('#organizer-status-info').hide();
            $('#organizer-loade-status').hide();
        }
    });

});

function Checkfiles(f){
    f = f.elements;
    if (f['c-file'].value === '') {
        swal('File error!', 'Please select a json files', 'error');
        f['c-file'].focus();
        return false;
    }
    if(/.*\.(json)$/.test(f['c-file'].value)) {
        return true;
    } else {
        swal('File error!', 'Please Upload json Files Only.', 'error');
        f['c-file'].focus();
        return false;
    }
};

// SETTINGS - HDD NAME
document.getElementById('hdd-name').onclick = function(){
    var curName = $('#hdd-name').text();
    swal({
        title: "HDD Name",
        text: 'Enter/Modify the HDD Name:',
        type: 'input',
        showCancelButton: true,
        closeOnConfirm: false,
        animation: "slide-from-top",
        inputPlaceholder: curName,
        inputValue: curName,
    },
    function(inputValue){
        if (inputValue === false) { return false; }

        if (inputValue === "") {
            swal.showInputError("The disk needs a name!!!");
            return false;
        }
        if (inputValue.match('^[0-9a-zA-Z_-]+$') === null ) {
            swal.showInputError("Only digits, letters, and underscores are allowed.");
            return false;
        }
        $.post( "/settings/", {
            hdd_name: inputValue,
        })
        .done(function(data) {
            if (data['done'] === true) {
                swal({   title: "Really change the HDD Name?",   text: "The HDD Name is used to identify this disk on the remote server, and when creating a diff against another disk. Changing the name can cause errors and name mismatches!",   type: "warning",   showCancelButton: true,   confirmButtonColor: "#DD6B55",   confirmButtonText: "Yes, change it!",   cancelButtonText: "No, turn back!",   closeOnConfirm: false,   closeOnCancel: false }, function(isConfirm){   if (isConfirm) {     swal("Changed!", "The HDD Name has been changed to " + inputValue, "success"); $('#hdd-name').text(inputValue);  } else {     swal("Cancelled", "The HDD Name has not been changed :)", "error");   } });
                return true;
            } else if (data['validation'] === true) {
                swal.showInputError("Server returned validation error.");
                return false;
            } else {
                swal("Error!", 'The server could not complete the request. Please check the terminal or logs for more details', "error");
                return false;
            }
        })
        .fail(function() { swal("Error!", 'The server could not complete the request. Please check the terminal or logs for more details', "error");
            return false; });

        //
    });
};

// SETTINGS - HDD ROOT
document.getElementById('hdd-root').onclick = function(){
    var curName = $('#hdd-root').text();
    swal({
        title: "HDD Root Path",
        text: 'Enter/Modify the HDD Root Path:',
        type: 'input',
        showCancelButton: true,
        closeOnConfirm: false,
        animation: "slide-from-top",
        inputPlaceholder: curName,
        inputValue: curName,
    },
    function(inputValue){
        if (inputValue === false) { return false; }

        if (inputValue === "") {
            swal.showInputError("The disk needs a root path!!!");
            return false;
        }
        $.post( "/settings/", {
            hdd_root: inputValue,
        })
        .done(function(data) {
            if (data['done'] === true) {
                $('#hdd-root').text(inputValue);
                swal("Nice!", 'Disk root path changed to: ' + inputValue, "success");
                return true;
            } else if (data['validation'] === true) {
                swal.showInputError("Server returned validation error.");
                return false;
            } else {
                swal("Error!", 'The server could not complete the request. Please check the terminal or logs for more details', "error");
                return false;
            }
        })
        .fail(function() { swal("Error!", 'The server could not complete the request. Please check the terminal or logs for more details', "error");
            return false; });

        //
    });
};

// SETTINGS - MOVIE FOLDER
document.getElementById('movie-folder').onclick = function(){
    var curName = $('#movie-folder').text();
    swal({
        title: "Movie Folder(s)",
        text: 'Enter/Modify Movie Folder(s) path:',
        type: 'input',
        showCancelButton: true,
        closeOnConfirm: false,
        animation: "slide-from-top",
        inputPlaceholder: curName,
        inputValue: curName,
    },
    function(inputValue){
        if (inputValue === false) { return false; }

        if (inputValue === "") {
            swal.showInputError("The movie folder(s) needs a path!!!");
            return false;
        }

        if (inputValue.lastIndexOf($('#hdd-root').text(), 0) !== 0) {
            swal.showInputError("The movie folder(s) should be within the hdd root!!!");
            return false;
        }
        $.post( "/settings/", {
            movie_folder: inputValue,
        })
        .done(function(data) {
            if (data['done'] === true) {
                $('#movie-folder').text(inputValue);
                swal("Nice!", 'Movie folder(s) path changed to: ' + inputValue, "success");
                return true;
            } else if (data['validation'] === true) {
                swal.showInputError("Server returned validation error.");
                return false;
            } else {
                swal("Error!", 'The server could not complete the request. Please check the terminal or logs for more details', "error");
                return false;
            }
        })
        .fail(function() { swal("Error!", 'The server could not complete the request. Please check the terminal or logs for more details', "error");
            return false; });

        //
    });
};

// CRAWLER
document.getElementById('crawler-switch').onclick = function(){
    $.get( "/crawler/", {'status': true,}, function(data) {
        if (data['status'] === true) {
            swal({
                    title: "Stop Crawler?",
                    text: "Do you really want to stop the crawler?",
                    type: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#DD6B55",
                    confirmButtonText: "Yes, stop it!",
                    cancelButtonText: "No, turn back!",
                    closeOnConfirm: true,
                    closeOnCancel: false,
                },
                function(isConfirm){
                   if (isConfirm) {
                        $.post( "/crawler/", {
                            'stop': true,
                        }, function(data) {
                            if (data['error'] == true) {
                                swal("Server Error", data['error_message'], "error");
                                return;
                            }
                            swal("Crawler status", "The crawler has been stopped.", "success");
                            $('#crawler-status').text('STOPPED');
                            $('#crawler-status').removeClass('label-success').addClass('label-danger');
                            $('#crawler-switch').text('Start Crawler');
                            $('#crawler-switch').removeClass('btn-danger').addClass('btn-success');
                            $('#crawler-status-info').removeClass('fa-spin');
                            $('#crawler-status-info').hide();
                            $('#crawler-crawl-status').hide();
                        });
                    }
                }
            );
        } else {
            swal({
                    title: "Start Crawler?",
                    text: "Do you really want to start the crawler?",
                    type: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#33FF33",
                    confirmButtonText: "Yes, start it!",
                    cancelButtonText: "No, turn back!",
                    closeOnConfirm: false,
                    closeOnCancel: true,
                },
                function(isConfirm){
                   if (isConfirm) {
                        $.post( "/crawler/", {
                            'start': true,
                        }, function(data) {
                            if (data['error'] == true) {
                                swal("Server Error", data['error_message'], "error");
                                return;
                            }
                            swal("Crawler status", "The crawler has been started.", "success");
                            $('#crawler-status').text('RUNNING');
                            $('#crawler-status').removeClass('label-danger').addClass('label-success');
                            $('#crawler-switch').text('Stop Crawler');
                            $('#crawler-switch').removeClass('btn-success').addClass('btn-danger');
                            $('#crawler-status-info').addClass('fa-spin');
                            $('#crawler-status-info').show();
                            $('#crawler-crawl-status').show();
                            var timer, delay = 1000;

                            timer = setInterval(function(){
                            $.get( "/crawler/", {'status': true,}, function(data) {
                                if (data['status']==false) {
                                    clearInterval( timer );
                                    $('#crawler-status').text('STOPPED');
                                    $('#crawler-status').removeClass('label-success').addClass('label-danger');
                                    $('#crawler-switch').text('Start Crawler');
                                    $('#crawler-switch').removeClass('btn-danger').addClass('btn-success');
                                    $('#crawler-status-info').removeClass('fa-spin');
                                    $('#crawler-status-info').hide();
                                    $('#crawler-crawl-status').hide();
                                    swal("Crawl complete!", "Files evaluated: " + data['files_evaluated'] + "\nMovies found: " + data['movies_found'] + "\nMovies added: " + data['movies_added'], "success");
                                } else {
                                    $('#crawler-files-evaluated').text(data['files_evaluated']);
                                    $('#crawler-movies-found').text(data['movies_found']);
                                    $('#crawler-movies-added').text(data['movies_added']);
                                }
                            });
                            }, delay);
                        });
                    }
                }
            );
        }
    });
};

// LOADER
document.getElementById('loader-switch').onclick = function(){
    $.get( "/loader/", {'status': true,}, function(data) {
        if (data['status'] === true) {
            swal({
                    title: "Stop Loader?",
                    text: "Do you really want to stop the Loader?",
                    type: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#DD6B55",
                    confirmButtonText: "Yes, stop it!",
                    cancelButtonText: "No, turn back!",
                    closeOnConfirm: false,
                    closeOnCancel: true,
                },
                function(isConfirm){
                   if (isConfirm) {
                        $.post( "/loader/", {
                            'stop': true,
                        }, function(data) {
                            if (data['error'] == true) {
                                swal("Server Error", data['error_message'], "error");
                                return;
                            }
                            swal("Organizer status", "The Loader has been stopped.", "success");
                            $('#loader-status').text('STOPPED');
                            $('#loader-status').removeClass('label-success').addClass('label-danger');
                            $('#loader-switch').text('Start loader');
                            $('#loader-switch').removeClass('btn-danger').addClass('btn-success');
                            $('#loader-status-info').removeClass('fa-spin');
                            $('#loader-status-info').hide();
                            $('#loader-load-status').hide();
                        });
                    }
                }
            );
        } else {
            swal({
                    title: "Start Loader?",
                    text: "Once started, the Loader will take a potentially significant amount of time downloading metadata from online sources.",
                    type: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#FF0000",
                    confirmButtonText: "Yes, start it!",
                    cancelButtonText: "No, turn back!",
                    closeOnConfirm: false,
                    closeOnCancel: true,
                },
                function(isConfirm){
                   if (isConfirm) {
                        $.post( "/loader/", {
                            'start': true,
                        }, function(data) {
                            if (data['error'] == true) {
                                swal("Server Error", data['error_message'], "error");
                                return;
                            }
                            swal("loader status", "The Loader has been started.", "success");
                            $('#loader-status').text('RUNNING');
                            $('#loader-status').removeClass('label-danger').addClass('label-success');
                            $('#loader-switch').text('Stop Loader');
                            $('#loader-switch').removeClass('btn-success').addClass('btn-danger');
                            $('#loader-status-info').addClass('fa-spin');
                            $('#loader-status-info').show();
                            $('#loader-load-status').show();
                            $('#loader-movies-evaluated').text(data['movies_evaluated']);
                            $('#loader-metadata-downloaded').text(data['metadata_downloaded']);
                            $('#loader-movies-skipped').text(data['movies_skipped']);
                            var timer, delay = 1000;

                            timer = setInterval(function(){
                            $.get( "/loader/", {'status': true,}, function(data) {
                                if (data['status']==false) {
                                    clearInterval( timer );
                                    $('#loader-status').text('STOPPED');
                                    $('#loader-status').removeClass('label-success').addClass('label-danger');
                                    $('#loader-switch').text('Start Loader');
                                    $('#loader-switch').removeClass('btn-danger').addClass('btn-success');
                                    $('#loader-status-info').removeClass('fa-spin');
                                    $('#loader-status-info').hide();
                                    $('#loader-load-status').hide();
                                    var skipped = data['skipped_list'];
                                    var displaylist = "<div id='box'>";
                                    for(var i=0; i<skipped.length; i++){
                                        displaylist+=skipped[i];
                                        displaylist+='<br />';
                                    }
                                    displaylist+="</div>";
                                    swal({
                                        title: "Loader complete!",
                                        text: "<strong>Movies evaluated:</strong> " + data['movies_evaluated'] + "<br /><strong>Metadata downloaded:</strong> " + data['metadata_downloaded'] + "<br /><strong>Movies skipped: </strong>" + data['movies_skipped'] + "<br />" + displaylist + "<br /><br />",
                                        type: "success",
                                        html: true,
                                    });
                                } else {
                                    $('#loader-movies-evaluated').text(data['movies_evaluated']);
                                    $('#loader-metadata-downloaded').text(data['metadata_downloaded']);
                                    $('#loader-movies-skipped').text(data['movies_skipped']);
                                }
                            });
                            }, delay);
                        });
                    }
                }
            );
        }
    });
};

// ORGANIZER
document.getElementById('organizer-switch').onclick = function(){
    $.get( "/organizer/", {'status': true,}, function(data) {
        if (data['status'] === true) {
            swal({
                    title: "Stop Organizer?",
                    text: "Do you really want to stop the Organizer?",
                    type: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#DD6B55",
                    confirmButtonText: "Yes, stop it!",
                    cancelButtonText: "No, turn back!",
                    closeOnConfirm: false,
                    closeOnCancel: true,
                },
                function(isConfirm){
                   if (isConfirm) {
                        $.post( "/organizer/", {
                            'stop': true,
                        }, function(data) {
                            if (data['error'] == true) {
                                swal("Server Error", data['error_message'], "error");
                                return;
                            }
                            swal("Organizer status", "The Organizer has been stopped.", "success");
                            $('#organizer-status').text('STOPPED');
                            $('#organizer-status').removeClass('label-success').addClass('label-danger');
                            $('#organizer-switch').text('Start organizer');
                            $('#organizer-switch').removeClass('btn-danger').addClass('btn-success');
                            $('#organizer-status-info').removeClass('fa-spin');
                            $('#organizer-status-info').hide();
                            $('#organizer-organize-status').hide();
                        });
                    }
                }
            );
        } else {
            swal({
                    title: "Start Organizer?",
                    text: "Once started, the Organizer will take a potentially significant amount of time downorganizing metadata from online sources.",
                    type: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#FF0000",
                    confirmButtonText: "Yes, start it!",
                    cancelButtonText: "No, turn back!",
                    closeOnConfirm: false,
                    closeOnCancel: true,
                },
                function(isConfirm){
                   if (isConfirm) {
                        $.post( "/organizer/", {
                            'start': true,
                        }, function(data) {
                            if (data['error'] == true) {
                                swal("Server Error", data['error_message'], "error");
                                return;
                            }
                            swal("organizer status", "The Organizer has been started.", "success");
                            $('#organizer-status').text('RUNNING');
                            $('#organizer-status').removeClass('label-danger').addClass('label-success');
                            $('#organizer-switch').text('Stop Organizer');
                            $('#organizer-switch').removeClass('btn-success').addClass('btn-danger');
                            $('#organizer-status-info').addClass('fa-spin');
                            $('#organizer-status-info').show();
                            $('#organizer-organize-status').show();
                            $('#organizer-files-evaluated').text(data['movies_evaluated']);
                            var timer, delay = 1000;

                            timer = setInterval(function(){
                            $.get( "/organizer/", {'status': true,}, function(data) {
                                if (data['status']==false) {
                                    clearInterval( timer );
                                    $('#organizer-status').text('STOPPED');
                                    $('#organizer-status').removeClass('label-success').addClass('label-danger');
                                    $('#organizer-switch').text('Start Organizer');
                                    $('#organizer-switch').removeClass('btn-danger').addClass('btn-success');
                                    $('#organizer-status-info').removeClass('fa-spin');
                                    $('#organizer-status-info').hide();
                                    $('#organizer-organize-status').hide();
                                    swal({
                                        title: "Organize complete!",
                                        text: "Your files are now Organized...!",
                                        type: "success",
                                        html: true,
                                    });
                                } else {
                                    $('#organizer-files-evaluated').text(data['files_evaluated']);
                                }
                            });
                            }, delay);
                        });
                    }
                }
            );
        }
    });
};

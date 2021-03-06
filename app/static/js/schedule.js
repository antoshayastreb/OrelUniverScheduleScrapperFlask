$(document).ready(function ()
{
    if (document.cookie.split(';').filter((item) => item.trim().startsWith('group=')).length) {
        var cookieGroup = document.cookie.replace(/(?:(?:^|.*;\s*)group\s*\=\s*([^;]*).*$)|^.*$/, "$1");
        console.log(cookieGroup)
        print_schedule(cookieGroup)
    }

    general();

    $('#calendarID').on('change', function() {
        var selectedItem = $(this).find(":selected").val();
        console.log(selectedItem);
        document.getElementById('overwriteEvents').innerHTML = '';
        if (selectedItem != 'new'){
            check_events_from_calendar(selectedItem);
        }
    });
});

function general() {
    $('body').on('click', 'button', function(){
        var el = $(this);
        console.log(el.attr('id'));
        var val = el.val();
        switch(el.attr('id')){
            case 'division':
                el.addClass('disabled').siblings().removeClass('disabled');
                var accordionBody = document.getElementById('kurs');
                console.log(accordionBody);
                accordionBody.innerHTML = '';
                kurslist(val);
                break;
            case 'kurs':
                el.addClass('disabled').siblings().removeClass('disabled');
                var accordionBody = document.getElementById('group');
                console.log(accordionBody);
                accordionBody.innerHTML = '';
                grouplist(val);
                break;
            case 'group':
                el.addClass('disabled').siblings().removeClass('disabled');
                var schedule_body = document.getElementById('tableforstuds');
                console.log(schedule_body);
                $('#aGroup').click();
                $('#tableforstuds').hide();
                schedule_body.innerHTML = '';
                print_schedule(val);
                break;
            case 'exportForStuds':
                var calendarItems_body = document.getElementById('calendarID');
                calendarItems_body.innerHTML = '';
                prepare_calendar_list();
                break;
            case 'cancelExport':
                document.getElementById('calendarID').innerHTML = '';
                document.getElementById('overwriteEvents').innerHTML = '';
                break;
            case 'prev':
                var schedule_body = document.getElementById('tableforstuds');
                schedule_body.innerHTML = '';
                var cookieGroup = document.cookie.replace(/(?:(?:^|.*;\s*)group\s*\=\s*([^;]*).*$)|^.*$/, "$1");
                print_schedule_prev(cookieGroup);
                break;
            case 'now':
                var schedule_body = document.getElementById('tableforstuds');
                schedule_body.innerHTML = '';
                var cookieGroup = document.cookie.replace(/(?:(?:^|.*;\s*)group\s*\=\s*([^;]*).*$)|^.*$/, "$1");
                print_schedule(cookieGroup);
                break;
            case 'next':
                var schedule_body = document.getElementById('tableforstuds');
                schedule_body.innerHTML = '';
                var cookieGroup = document.cookie.replace(/(?:(?:^|.*;\s*)group\s*\=\s*([^;]*).*$)|^.*$/, "$1");
                print_schedule_next(cookieGroup);
                break;
        }
    })
}

function kurslist(division_id){
    $.ajax({
       url: "/get_kurslist",
       type: "POST",
       dataType: "json",
       data: {'division_id':division_id},
       success: function(resp){
         $('#kurs').append(resp.data);
         $('#aKurs').click();
       }
      });
}

function grouplist(kurs){
    $.ajax({
       url: "/get_grouplist",
       type: "POST",
       dataType: "json",
       data: {'kurs':kurs},
       success: function(resp){
         $('#group').append(resp.data);
         $('#aGroup').click();
       }
      });
}

function print_schedule(group){
    $.ajax({
       url: "/print_student_schedule",
       type: "POST",
       dataType: "json",
       data: {'group':group},
       success: function(resp){
         $('#tableforstuds').append(resp.data);
         $('#tableforstuds').show();
       }
      });
}

function print_schedule_prev(group){
    $.ajax({
       url: "/print_student_schedule_prev",
       type: "POST",
       dataType: "json",
       data: {'group':group},
       success: function(resp){
         $('#tableforstuds').append(resp.data);
         $('#tableforstuds').show();
       }
      });
}

function print_schedule_next(group){
    $.ajax({
       url: "/print_student_schedule_next",
       type: "POST",
       dataType: "json",
       data: {'group':group},
       success: function(resp){
         $('#tableforstuds').append(resp.data);
         $('#tableforstuds').show();
       }
      });
}

function prepare_for_export(){
    $.ajax({
       url: "/prepare_for_export",
       type: "GET",
       dataType: "json",
       success: function(resp){
         $('#calendarItems').append(resp.data);
       }
      });
}

function prepare_calendar_list(){
    $.ajax({
       url: "/prepare_calendar_list",
       type: "GET",
       dataType: "json",
       success: function(resp){
          $('#calendarID').append(resp.data);
          var calendarID = $( "select option:selected " ).attr('value');
                if (calendarID != 'new'){
                    check_events_from_calendar(calendarID);
                }
       }
      });
}

function check_events_from_calendar(calendarID){
    var exportButton = document.getElementById('studsExport');
    $('#studsExport').addClass('disabled');
    $.ajax({
       url: "/check_events",
       type: "POST",
       dataType: "json",
       data: {'calendarID':calendarID},
       success: function(resp){
            $('#overwriteEvents').append(resp.data);
            $('#studsExport').removeClass('disabled');
       }
      });
}
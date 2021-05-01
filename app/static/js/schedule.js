$(document).ready(function ()
{
    general();
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
                var modaltable_body = document.getElementById('schedule_events');
                var calendarItems_body = document.getElementById('calendarItems');
                calendarItems_body.innerHTML = '';
                modaltable_body.innerHTML = '';
                prepare_for_export();
                prepare_calendar_list();

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
          $('#calendarItems').append(resp.data);
       }
      });
}
$(document).ready(function ()
{
    divisionlist();
    prepare_calendar_list();

    $(document).on('change', function() {
        $('#savePersonal').removeClass('disabled');
    });

    $('#personaldivision').on('change', function() {
        var selectedItem = $(this).find(":selected").val();
        console.log(selectedItem);
        document.getElementById('personalkurs').innerHTML = '';
        kurslist(selectedItem);
    });
    $('#personalkurs').on('change', function() {
        var selectedItem = $(this).find(":selected").val();
        console.log(selectedItem);
        document.getElementById('personalgroup').innerHTML = '';
        grouplist(selectedItem);
    });

    $('#flexSwitchCheck').on('change.bootstrapSwitch', function(e) {
        if (e.target.checked){
            $('#checklabel').text('Авто обновление включено');
        }
        else{
            $('#checklabel').text('Авто обновление выключено');
        }

    });
});

function divisionlist(){
    $.ajax({
       url: "/get_divisionlist",
       type: "GET",
       dataType: "json",
       success: function(resp){
         $('#personaldivision').append(resp.data);
       }
      });
}

function kurslist(division_id){
    $.ajax({
       url: "/get_personalkurslist",
       type: "POST",
       dataType: "json",
       data: {'division_id':division_id},
       success: function(resp){
         $('#personalkurs').append(resp.data);
         var selectedKurs = $('#personalkurs').find(":selected").val();
         document.getElementById('personalgroup').innerHTML = '';
         grouplist(selectedKurs);
       }
      });
}

function grouplist(kurs){
    $.ajax({
       url: "/get_personalgrouplist",
       type: "POST",
       dataType: "json",
       data: {'kurs':kurs},
       success: function(resp){
         $('#personalgroup').append(resp.data);
       }
      });
}

function prepare_calendar_list(){
    $.ajax({
       url: "/prepare_personalcalendar_list",
       type: "GET",
       dataType: "json",
       success: function(resp){
          $('#personalcalendar').append(resp.data);
       }
      });
}
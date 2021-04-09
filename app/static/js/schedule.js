$(document).ready(function ()
{
    general();
});

function general() {
    $('body').on('click', '.btn', function(){
        var el = $(this);
        console.log(el.parent().attr('id'));
        el.addClass('disabled').siblings().removeClass('disabled');
        var val = el.val();
        switch(el.parent().attr('id')){
            case 'divisions':
                var accordionBody = document.getElementById('kurs');
                console.log(accordionBody);
                accordionBody.innerHTML = '';
                kurslist(val);
                $('#accordionKurs').click();
            case 'kurs':
                var accordionBody = document.getElementById('group');
                console.log(accordionBody);
                accordionBody.innerHTML = '';
                grouplist(val);
                $('#accordionGroup').click();
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
       }
      });
}
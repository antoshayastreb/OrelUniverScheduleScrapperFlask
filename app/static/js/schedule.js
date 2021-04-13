$(document).ready(function ()
{
    general();
});

function general() {
    $('body').on('click', 'button', function(){
        var el = $(this);
        console.log(el.attr('id'));
        el.addClass('disabled').siblings().removeClass('disabled');
        var val = el.val();
        switch(el.attr('id')){
            case 'division':
                var accordionBody = document.getElementById('kurs');
                console.log(accordionBody);
                accordionBody.innerHTML = '';
                kurslist(val);
                break;
            case 'kurs':
                var accordionBody = document.getElementById('group');
                console.log(accordionBody);
                accordionBody.innerHTML = '';
                grouplist(val);
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
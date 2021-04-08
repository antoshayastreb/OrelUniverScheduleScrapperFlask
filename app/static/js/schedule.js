$(document).ready(function ()
{
    general();
});

function general() {
    $('.btn').on('click', function(){
        var el = $(this);
        console.log(el.parent().attr('id'));
        el.siblings().addClass('disabled');
        var val = el.data('value');
        switch(el.parent().attr('id')){
            case 'divisions':
                $('#kurs .accordion-body').children().remove();
                kurslist(val);
                $('#accordionKurs').click()

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
         $('#kurs .accordion-body').append(resp.data);
       }
      });
}
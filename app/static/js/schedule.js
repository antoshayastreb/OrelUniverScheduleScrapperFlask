$(document).ready(function ()
{
    general();
});

function general() {
    $('class.tab-content class.accordion-body class.btn').on("click", function(){
        var el = $(this);
        el.addClass('active').siblings().removeClass('active');
    })
}


$(document).ready(function(){
    reorganizeForm();

    if($(document).find('#id_is_for_internal').length == 1) {
        $('#id_is_for_internal').click(function(){
            reorganizeForm();
        });
    }
})


function reorganizeForm()
{

    if($('#id_is_for_internal:checked').val() == 'on'){
        $('div.field-partner').hide();
        $('div.field-pca').hide();
        $('div.field-partnership_start_date').hide();
        $('div.field-partnership_end_date').hide();
    }else{
        $('div.field-partner').show();
        $('div.field-pca').show();
        $('div.field-partnership_start_date').show();
        $('div.field-partnership_end_date').show();

    }

}

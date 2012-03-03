$(document).ready(function(){
    var set_fields_visibility = function(day_week, day_month) {
        if( day_week == 0) {
            $('select#id_send_day_week').parent('p').css('display', 'none');
        }
        else {
            $('select#id_send_day_week').parent('p').css('display', 'block');
        }
        if( day_month == 0) {
            $('select#id_send_day_month').parent('p').css('display', 'none');
        }
        else {
            $('select#id_send_day_month').parent('p').css('display', 'block');
        }
    }

    var switch_period = function(){
        switch( $('select#id_period').val() ){
            case '0':
                set_fields_visibility(0, 0); break;
            case '1':
                set_fields_visibility(1, 0); break;
            case '2':
                set_fields_visibility(0, 1); break;
        }
    }

    switch_period();

    $('select#id_period').change(function(e){
        switch_period();
    });
});
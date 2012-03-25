$(document).ready(function(){
    var global_search = {};

    global_search.form = $('form.global-search');
    global_search.submit = $(global_search.form).find('a.submit').first();
    global_search.input = $(global_search.form).find('input[name=s]').first();

    global_search.input_val = $(global_search.input).val();

    $(global_search.input).focusin(function(){
        $(this).val('');
    });

    $(global_search.input).focusout(function(){
        $(this).val(global_search.input_val)
    });

    $(global_search.submit).click(function(){
        $(global_search.form).submit();
        return false;
    });
});


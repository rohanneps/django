$(document).ready(function() {
    $('#detailform')[0].reset();

    var xpath_flag = true;
    var url_flag = true;
    var platform_flag = true;

    $('#err_count_error').hide();

    $('#id_run_priority').change(function (e) {
        if ($('#detailform')[0][4].options.selectedIndex == 0) {
            $('#max_err_count').show();
        } else {
            $('#max_err_count').hide();
        }
    });

    $('#xpath_file_error').hide();
    $('#url_file_error').hide();
    $('#platform_import_file_error').hide();

    $('#id_xpath_file').blur(function (e) {
        if (!$('#id_xpath_file')[0].files[0].name.endsWith('.csv')) {
            xpath_flag = false;
            $('#xpath_file_error').show();
        } else {
            xpath_flag = true;
            $('#xpath_file_error').hide();
        }
    });

    $('#id_url_file').blur(function (e) {
        if (!$('#id_url_file')[0].files[0].name.endsWith('.csv')) {
            url_flag = false;
            $('#url_file_error').show();
        } else {
            url_flag = true;
            $('#url_file_error').hide();
        }
    });

    $('#id_platform_import_file').blur(function (e) {
        if (!$('#id_platform_import_file')[0].files[0].name.endsWith('.csv')) {
            platform_flag = false;
            $('#platform_import_file_error').show();
        } else {
            platform_flag = true;
            $('#platform_import_file_error').hide();
        }
    });

    $('#detailformsubmitbutton').click(function (e) {
        sessionStorage.setItem("alert_count", 0);
        var val = $('#err_count_val')[0].value;
        err_count_is_not_num = isNaN(val);
        if (xpath_flag && url_flag && platform_flag){
            if ($('#detailform')[0][4].options.selectedIndex == 0) {
                if (val && !err_count_is_not_num) {
                    $('#err_count_error').hide();
                    return true;
                }
                else {
                    $('#err_count_error').show();
                    return false;
                }
            }
            else{
                return true;
            }
        }
        else if (!xpath_flag || !url_flag || !platform_flag){
            return false;
        }
    });
});
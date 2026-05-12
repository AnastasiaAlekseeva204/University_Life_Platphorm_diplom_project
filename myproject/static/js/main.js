$(document).ready(function() {
    console.log('привет мир')
    $('.role_select').on('change', function() {
        var role = $(this).val();
        if (role == 'STUDENT'){
            $('.role_cours').show();
        }
        else{
           $('.role_cours').hide();
        }
    }); 
});

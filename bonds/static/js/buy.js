function price_valid() {
	var price = parseFloat($('#id_price').val());
	if (isNaN(price)) {
			  price = 0;
			};
	if (price <= 0){
			$('#id_price').addClass('is-invalid');
		  $('#sm_price').collapse('show');
		  return false
		}else{
			$('#id_price').removeClass('is-invalid');
		  $('#sm_price').collapse('hide');
		  return true
		};
};
function comission_valid() {
	var comission = parseFloat($('#id_comission').val());
	if (isNaN(comission)) {
				  comission = 0;
				};
	if (comission < 0){
			$('#id_comission').addClass('is-invalid');
		  $('#sm_comission').collapse('show');
		  return false
		}else{
			$('#id_comission').removeClass('is-invalid');
		  $('#sm_comission').collapse('hide');
		  return true
		};

};
function count_valid() {
	var count = parseFloat($('#id_count').val());
	if (isNaN(count)) {
				  count = 0;
				};
	if (count <= 0){
		$('#id_count').addClass('is-invalid');
	  $('#sm_count').text('Значение должно быть больше 0.');
	  $('#sm_count').collapse('show');
	  return false
	}else{
		$('#id_count').removeClass('is-invalid');
	  $('#sm_count').collapse('hide');
	  return true
	};
};
function result() {
	var price = parseFloat($('#id_price').val());
	var count = parseFloat($('#id_count').val());
	var comission = parseFloat($('#id_comission').val());
	var action = ($('#action').val() == 'Продажа');
	var nkd = parseFloat($('#id_nkd').val());
	if (isNaN(price)) {
		  price = 0;
		};
	if (isNaN(nkd)) {
		  nkd = 0;
		};
	if (isNaN(count)) {
	  count = 0;
	};
	if (isNaN(comission)) {
	  comission = 0;
	};
	if (action){
		comission = comission * (-1);
	};
	res = price * count + comission + nkd
	$('#cost').val(res);
	return res
};

$(function(){
	$('#sm, #sm_count, #sm_price, #sm_comission, #sm_nkd').collapse({
			toggle: false
	});
	$('#id_portfolio').change(function () {
		var security = $('#security_id').val()
		var portfolio = $('#id_portfolio').val()
		if (typeof security === "undefined") {
			$('#ostatok').text($('#id_portfolio option:selected').attr('ostatok'));
		}else{
			$.get(
		    	'/securities/sp/' + portfolio + '/' + security + '/',
		        function(data){
		            if (data['status'] == 'ok'){
		            	$('#ostatok').text(data['ostatok'])
		            	$('#ostatok_sec').text(data['ostatok_sec'])
		            	$('#id_count').keyup();
		            }
		            
		        }
	    	);
		};

	});
	var action = ($('#action').val() == 'Продажа');
	if (action) {
		$('#id_count, #id_price, #id_comission, #id_nkd').keyup(function(){
			res = result()
			var count = parseFloat($('#id_count').val());
			var ostatok_sec = parseFloat($('#ostatok_sec').text());
			if (isNaN(count)) {
		  		count = 0;
			};
			var cost = $('#cost').val();
			if (isNaN(cost)) {
		  		cost = 0;
			};
			if (cost < 0) {
				c = false;
			}else{
				c = true;
			};
			if (count > ostatok_sec) {
				$('#sm_count').text('Недостаточно бумаг для продажи.');
		  	$('#sm_count').collapse('show');
				v = false;
			}else{
				v = true;
				$('#sm_count').collapse('hide');
			};
			pv = price_valid();
			cv = comission_valid();
			c_v = count_valid();
			if (c && v && pv && cv && c_v){
				$('#sub').prop('disabled', false);
				$('#cost').removeClass('is-invalid');
			}else{
				$('#sub').prop('disabled', true);
				$('#cost').addClass('is-invalid');
			};
		});
	}else{
		$('#id_count, #id_price, #id_comission, #id_nkd').keyup(function(){
			
		var price = parseFloat($('#id_price').val());
		var count = parseFloat($('#id_count').val());
		var comission = parseFloat($('#id_comission').val());
		var ostatok = parseFloat($('#ostatok').text());
		var nkd = parseFloat($('#id_nkd').val());
		if (isNaN(price)) {
		  price = 0;
		};
		if (isNaN(nkd)) {
		  nkd = 0;
		};
		if (isNaN(comission)) {
		  comission = 0;
		};
		if (isNaN(count)) {
		  count = 0;
		};
		res = price * count + comission + nkd
		 $('#cost').val(res);
		if (res > ostatok){
		  $('#sm').collapse('show');
		  $('#cost').addClass('is-invalid');
		  v = false;
		}else{
		  $('#sm').collapse('hide');
		  $('#cost').removeClass('is-invalid');
		  v = true;
		  };
		  pv = price_valid();
		  cv = comission_valid();
		  c_v = count_valid();
	  if (v && pv && cv && c_v){
			$('#sub').prop('disabled', false);
		}else{
			$('#sub').prop('disabled', true);
		};
		
	  });
	};
});

$(function(){
	  $('#id_date').daterangepicker({
		  singleDatePicker: true,
			  locale: {
				  format: 'DD.MM.YYYY'
									  }
								  });
			  });
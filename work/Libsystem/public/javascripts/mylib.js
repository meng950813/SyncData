//借书、还书、续借、预约、取消预约等界面所需的js代码
//借书请求
$(document).ready(function() {
	$('#borrow').click(function() {
		var isbn = $("#isbn").text();
		var readerId = $("#readerId").val();

		if (isbn == "" || readerId == "") {
			alert("学号 或 书号获取失败");
			return;
		}
		$.StandardPost("/borrow", {
			isbn: isbn,
			readerId:readerId
		});
	});
});

//还书请求
// $(document).ready(function() {
// 	$(".return").each(function(index) {
// 		$(".return").eq(index).click(function() {
// 			var url = "/mylib/return";
// 			var barcode = $(".barcode").eq(index).text();
// 			$.StandardPost(url, {
// 				barcode: barcode
// 			});
// 		});
// 	});
// });

//预约请求
$(document).ready(function() {
	$('#order').click(function() {
		var isbn = $("#isbn").text();
		var readerId = $("#readerId").val();

		if (isbn == "" || readerId == "") {
			alert("学号 或 书号获取失败");
			return;
		}

		$.StandardPost("/order", {
			isbn: isbn,
			readerId,readerId
		});
	});
});

// //续借请求
// $(document).ready(function() {
// 	$(".renew").each(function(index) {
// 		$(".renew").eq(index).click(function() {
// 			var url = "/mylib/renew";
// 			var barcode = $(".barcode").eq(index).text();
// 			$.StandardPost(url, {
// 				barcode: barcode
// 			});
// 		});
// 	});
// });

//取消预约
$(document).ready(function() {

	document.body.addEventListener('click', function(e){
		// e.preventDefault();
		var target = e.target;
		console.log(target)
		// 取消预约
		if(target.classList.contains('cancel')){
			fun(target.getAttribute('data'),"/cancel");
		}

		// TODO 续借
		else if(target.classList.contains('renew')){
			console.log("renew.data  "+ target.getAttribute('data'))
			fun(target.getAttribute('data'),"/renew_borrow");
		}

		// TODO 还书
		else if(target.classList.contains('return')){
			console.log("return.data  "+ target.getAttribute('data'))
			fun(target.getAttribute('data'),"/return_borrow");
		}
	}, false); 
});


function fun(tid,url){
	if (!tid) {
		alert("预约id获取失败: "+tid);
		return;
	}
	console.log(url,tid)
	$.StandardPost(url, {
		id : tid
	});
}


//构建post请求
$.extend({
	StandardPost: function(url, args) {
		var form = $("<form method='post'></form>");
		var input;
		form.attr({
			"action": url
		});
		$.each(args, function(key, value) {
			input = $("<input type='hidden'>");
			input.attr({
				"name": key
			});
			input.val(value);
			form.append(input);
		});
		form.appendTo(document.body);
		form.submit();
		document.body.removeChild(form[0]);
	}
});
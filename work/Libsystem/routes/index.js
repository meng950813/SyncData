var express = require('express');
var router = express.Router();
// var User=require('../models/user');
var Book=require('../models/book');
var Borrow=require('../models/borrow');
var Order=require('../models/order');

//跳转搜索页
router.get('/',function(req,res){
	res.redirect('/index');
});

//获取书目检索页
router.get('/index',function(req,res){
	res.render('index',{
		title:'书目检索',
		arr:[{sch:'active',lib:'',abt:'',log:''}]
	});
});

//处理书目检索请求
router.get('/search',function(req,res,next) {
	// console.log("this is search");
	var searchType = req.query.sType;//搜索类型
	var bookType = req.query.bType;//书籍类型
	var content = req.query.content;//搜索内容
	
	// console.log('content',content);

	Book.findBooksByTitle(content,function(err,books){
		if(err){
			return next(err);//使用return XXX 的写法是为了在发错误时不会出现res重复响应状况 
		}
		
		res.render('book_list',{
			title:'搜索结果',
			arr:[{sch:'active',lib:'',abt:'',log:''}],
			books:books,
		});
	});
});


//获得书籍详情 
router.get('/borrow',function(req,res,next){

	var book_list=req.query['list'];
	
	Book.findBooksByList(book_list,function(err,bookInfo){
		if(err){
			return next(err);
		}
		var oneBook = bookInfo[0];
		var canBorrow = 0;

		bookInfo.forEach(function(book){
			if(book.status == '1'){
				oneBook.isbn = book.isbn;
				canBorrow++;
			}
		});
		// 有书能借
		if(canBorrow){
			oneBook.canBorrow = canBorrow;
		}

		res.render('history',{
			title:'借阅',
	 		arr:[{sch:'',lib:'active',abt:'',log:''}],
	 		book:oneBook
	 	});
	});
});

//提交借书请求
router.post('/borrow',function(req,res,next){
	var readerId=req.body.readerId;// 学号
	var isbn = req.body.isbn;//书号

	console.log("post borrow :  "+readerId+"   "+isbn);

	if (readerId == undefined || isbn == undefined) return;
	
	
	Borrow.save(readerId,isbn,function(err,result=0){
		if (err) { 
			return next(err);
		}

		
		var msg = ["借书失败：学号错误,查无此人","借书成功!","借书失败: 此书不可借",'失败： 重复借书'];
		
		res.render('result',{
			title:'借阅结果',
		 	arr : [{sch:'active',lib:'',abt:'',log:''}],
		 	msg : msg[result]
		});
	});
});

// TODO 提交还书请求
router.post("/return_borrow",function(req,res,next){
	console.log("this is return_borrow "+ res.body.id)
	var book_id = res.body.id;

	Borrow.returnBook(book_id,function(err){
		if (err) {
			console.log("index.js  return_borrow  " + err)
			return next(err);
		}
		res.render("result",{
			title:'还书结果',
		 	arr : [{sch:'',lib:'active',abt:'',log:''}],
		 	msg : "还书成功"
		});
	})
});

// TODO 提交续借请求
router.post("/renew_borrow",function(req,res,next){
	var bor_id = res.body.id;
	Borrow.renew(bor_id,function(err){
		if (err) {
			console.log("index.js  renew_borrow  " + err)
			return next(err);
		}
		res.render("result",{
			title:'续借结果',
		 	arr : [{sch:'',lib:'active',abt:'',log:''}],
		 	msg : "续借成功"
		});
	})
})

// TODO 获取全部借阅历史
router.get("/history",function(req,res,next){
	console.log(res.query)
	var type = -1,uid = undefined;
	if(res.query){
		type = res.query['t'];
		uid = res.query['id'];
		
	}

	console.log("index.js : history ")
	console.log(type,uid)

	Borrow.findHistory(type,uid,function(err,Info){
		if(err){
			console.log("index.js: router.get history 获取全部借阅历史")
			return next(err);
		}
		console.log("获取全部借阅历史")
		console.log(Info);
		Info.forEach(function(his){
			his.outDate = fmtDate(his.outDate);
			// 是否已续借
			his.hasRenew = false;
			if(his.inDate) {
				his.inDate = fmtDate(his.inDate);
			}
			if(his.his_status == "2"){
				his.inDate += "  续借";
				his.hasRenew = true;
			}
		})

		res.render("history",{
			title:'借阅历史',
			arr:[{sch:'',lib:'active',abt:'',log:''}],
			// hasRecord : hasRecord,
			Info:Info
		})
	});
});

//跳转预约界面
router.get('/reserve',function(req,res,next){
	var uid=req.query['uid'];
	var start = req.query["s"];
	var fun , par;
	if(uid){
		par = uid;
		fun = Order.findOrderByreaderId;
	}
	else{
		par = start == undefined?0:start;
		fun = Order.findAllOrder;
	}
	console.log(fun)
	fun(par,function(err,Info){
		if(err){
			console.log("this err in index.js: router.get reserve 跳转预约界面")
			return next(err);
		}
		console.log("跳转预约界面：  ")
		console.log(Info)
		// var hasRecord = false
		Info.forEach(function(record){
			// hasRecord = true;
			if(record.res_status == 1){
				record.status = "等待序列";
				record.can_cancel = true;
			}else if(record.res_status == 2){
				record.status = "成功借书";
				record.can_cancel = false;
			}else{
				record.status = "预约取消";
				record.can_cancel = false;
			}
			record.res_date = fmtDate(record.res_date)
		});
		res.render('reserve',{
			title:'预约列表',
			arr:[{sch:'',lib:'',abt:'active',log:''}],
			// hasRecord : hasRecord,
			Info:Info
		});
	});
});

//发送预约请求
router.post('/order',function(req,res,next){
	var readerId=req.body.readerId;// 学号
	var book_list = req.body.isbn;//书号


	Order.save(readerId,book_list,function(err,result = 0){
		if (err) {
			return next(err);
		}

		var msg = ["预约失败：查无此人", "预约成功","有书，约个篮子","重复预约"]
		res.render('result',{
			title:'预约结果',
			arr : [{sch:'',lib:'',abt:'active',log:''}],
			msg : msg[result]
		});
	});
});

// 取消预约
router.post('/cancel',function(req,res,next){
	// console.log("this is post cancel aim")
	var res_id = req.body.id; // 预约编号

	Order.cancel(res_id,function(err){
		if (err) {
			return next(err);
		}
		res.render("result",{
			title : "取消预约",
			arr : [{sch:'',lib:'',abt:'active',log:''}],
			msg : "取消成功"
		});
	});
});


module.exports = router;

function fmtDate(obj){
    var date =  new Date(obj);
    var y = 1900+date.getYear();
    var m = "0"+(date.getMonth()+1);
    var d = "0"+date.getDate();
    return y+"-"+m.substring(m.length-2,m.length)+"-"+d.substring(d.length-2,d.length);
}
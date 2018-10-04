var db=require('./dbhelper');

//预约操作
var Order={};

module.exports=Order;

//预约 
Order.save=function(readerId,isbn,callback){
	db.getConnection(function(err,connection){
		if(err){
			return callback(err);
		}
		connection.beginTransaction(function(err){
			if(err){
				return callback(err);
			}
    		// 参数：book_list:书籍编号, uid:借书人学号,time,返回值result
    		// 返回值：0:查无此人，1：成功； 2：有书，不用约
    		var sql = "call book_reserve(?,?,?,@result)";

			connection.query(sql,[isbn,readerId,(new Date()).valueOf()],function(err,rows){

				if(err){
					return connection.rollback(function(){
						console.log("this is order.js Order.save,");
						callback(err);
					});
				}

				var sql = "SELECT @result",result = 0;
				connection.query(sql,[],function(err,row){
					result = row[0]['@result']
					// console.log("SELECT result "+result)
					// console.log(readerId,row)
				})
				connection.commit(function(err){
					if(err){
						console.log("this is  order.js; Order.save commit ");
						return connection.rollback(function(){
							callback(err);
						});
					}
					connection.end();
					callback(err,result);
				});
			});
		});
	});
};


// 所有预约情况
Order.findAllOrder = function(start,callback){
	var sql = "SELECT *,reservation.status as res_status FROM reservation,book,reader WHERE res_book_id = isbn and res_reader_id=reader_id order by reservation.status,res_date desc limit ?,?";
	db.exec(sql,[start,start+50],function(err,rows){
		if(err){
			return callback(err);
		}
		callback(err,rows);
	});
};

//根据证件号查找预约信息
Order.findOrderByreaderId = function(readerId,callback){
	var sql="SELECT *,reservation.status as res_status FROM reservation,book,reader WHERE res_reader_id=?  and res_book_id = isbn and res_reader_id=reader_id order by reservation.status";
	db.exec(sql,[readerId],function(err,rows){
		if(err){
			return callback(err);
		}
		callback(undefined,rows);
	});
};

//取消预约
Order.cancel=function(res_id,callback){
	var sql="UPDATE reservation set status='3' WHERE res_id=?";
	db.exec(sql,[res_id],function(err){
		if(err){
			return callback(err);
		}
		callback(undefined);
	});
};

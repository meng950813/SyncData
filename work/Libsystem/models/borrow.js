var db = require('./dbhelper');

function Borrow(readerId, book_id) {
	this.readerId = readerId;
	this.book_id = book_id;
}

module.exports = Borrow;

//保存借书记录
Borrow.save = function(readerId, book_id, callback) {
	db.getConnection(function(err,connection){
		if(err){
			return callback(err);
		}
		
		connection.beginTransaction(function(err){
			if(err){
				return callback(err);
			}

			// 借书参数： 书籍id, 用户id, 时间戳 , 返回值
			// 返回值意义： 0：查无此人 		1：借书成功		2：此书不可借 	3：重复借书
			// 
			var sql = "call book_borrow(?,?,?,@result)";
			var time = (new Date()).valueOf();
			console.log("借书时间 ： "+time);
			connection.query(sql,[book_id,readerId,time],function(err,rows){
				if(err){
					return connection.rollback(function(){
						callback(err);
					});
				}
				var result,sql = "SELECT @result;";
				connection.query(sql,[],function(err,row){
					console.log(row,row[0]["@result"])
					result = row[0]["@result"]
				});

				connection.commit(function(err){
					if(err){
						return connection.rollback(function(){
							callback(err);
						});
					}

					console.log(result);

					connection.end();
					callback(err,result);
				});
			})
		});
	});
};

// 查询(某人/所有)借阅情况
// type: -1:全部  0：未还  1：已还  3 遗失
Borrow.findHistory=function(type,uid,callback){
	var sql = "SELECT *,borrow_history.status as his_status,book.isbn as his_isbn, reader.reader_id as uid from borrow_history,book,reader WHERE borrow_history.isbn = book.isbn and borrow_history.reader_id = reader.reader_id ";
	var parm = [];
	if(type!= undefined && type != -1){
		console.log("borrow.js findHistory type = "+type)
		sql += " and status = ?";
		parm.push(type);
	}
	if(uid){
		sql += " and uid=?";
		parm.push(uid)
	}
	sql += "  ORDER BY outDate DESC";
	console.log("this is borrow.js  Borrow.findHistory")
	console.log(sql)
	console.log(parm)

	db.exec(sql,parm,function(err,rows){
		if(err){
			console.log("borrow.js   sql query")
			return callback(err);
		}
		callback(err,rows);
	});
}

//还书
Borrow.returnBook=function(book_id,callback){
	db.getConnection(function(err,connection){
		if(err){
			console.log("borrow.js  Borrow.returnBook connection error")
			return callback(err);
		}

		connection.beginTransaction(function(err){
			if (err) {
				return callback(err);
			}

			// 参数： book_id,time
			var sql = "call book_return(?,?)"
			connection.query(sql,[book_id,(new Date()).valueOf()],function(err,rows){
				if(err){
					console.log("borrow.js  Borrow.returnBook query error")

					return connection.rollback(function(){
						callback(err);
					});
				}
				connection.commit(function(err){
					if(err){
						console.log("borrow.js  Borrow.returnBook commit error")

						return connection.rollback(function(){
							callback(err);
						});
					}
					connection.end();
					callback(undefined);
				});
			})
		});
	});
};

//续借
Borrow.renew=function(bor_id,callback){
	db.getConnection(function(err,connection){
		if(err){
			console.log("borrow.js  renew connection error")
			return callback(err);
		}
		connection.beginTransaction(function(err){
			if(err){
				console.log("borrow.js  renew connection error-2")
				return callback(err);
			}
			
			// bor_id,time
			var sql = "call book_rebo(?,?)";
			connection.query(sql,[bor_id,new Date().valueOf()],function(err,rows){
				if(err){
					console.log("borrow.js  renew query error")
					return connection.rollback(function(){
						callback(err);
					});
				}

				connection.commit(function(err,rows){
					if(err){
						console.log("borrow.js  renew commit error")
						return connection.rollback(function(){
							callback(err);
						});
					}
					callback(err,rows);
				});	
			});
		});
	});
};

//历史借阅
// Borrow.findHistory=function(reader_id,callback){
// 	var sql="SELECT * from borrow_history WHERE  reader_id=? ORDER BY outDate DESC";
// 	db.exec(sql,[reader_id],function(err,rows){
// 		if(err){
// 			return callback(err);
// 		}
// 		callback(err,rows);
// 	});
// };

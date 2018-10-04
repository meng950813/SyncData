var db=require('./dbhelper');

//book类
function Book(){
	this.isbn;
	this.book_list;
	this.title;
	this.author;
	this.type;
	this.press;
	this.state;
}

module.exports=Book;

//保存书籍信息--后台使用的方法
Book.prototype.save = function() {
	var sql="";
};

//根据书名查找书
Book.findBooksByTitle=function(title,callback){
	var sql = "SELECT * FROM book WHERE title LIKE '%" + title + "%' group by book_list;";
	db.exec(sql,[],function(err,rows){
		if(err){
			return callback(err);
		}
		console.log("findBooksByTitle:  ");
		console.log(rows);

		//rows是一个对象数组
		callback(err,rows);
	});
};

//根据list查找书籍
Book.findBooksByList = function(book_list,callback){
	var sql = "SELECT * FROM book WHERE book_list = ?";
	db.exec(sql,[book_list],function(err,rows){
		if(err){
			return callback(err);
		}
		
		console.log("book findBooksByList: ");
		console.log(rows);

		//rows是一个对象数组
		callback(err,rows);
	});
};



// 查找所有书
Book.findBooks = function(callback){
	var sql = "SELECT * FROM book";
	db.exec(sql,[],function(err,rows){
		if(err){
			return callback(err);
		}
		
		console.log("book findBooks: ");
		console.log(rows);

		//rows是一个对象数组
		callback(err,rows);
	});
};

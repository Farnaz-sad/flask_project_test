from flask import Flask , request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///library.db'
data_base = SQLAlchemy(app)

class Library (data_base.Model):
    id = data_base.Column(data_base.Integer, primary_key=True)
    title = data_base.Column(data_base.String(250), nullable = False)
    author = data_base.Column(data_base.String(250), nullable = False)

    def __repr__(self):
        return f"<Book '{self.title}' , '{self.author}'> "


@app.route('/')
def homepage():
    return "Welcome to the Homepage!"  


@app.route('/greeting/<name>')
def agreet(name):
    return f"Hello, {name}! Welcome to Flask "  

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        book_title = request.form["title"]
        book_author = request.form['author']
        new_task = Library(title=book_title, author=book_author)
        wait_time = 3000
        seconds = wait_time / 1000
        redirect_url = '/all_books'
        try:
            data_base.session.add(new_task)
            data_base.session.commit()

            return f'''<html><body><p>book '{book_title}' By '{book_author}' has been added!</p>
            You will be redirected in { seconds } seconds</p>
            <script>var timer = setTimeout(function() {{window.location='{ redirect_url }'}},
            { wait_time });</script></body></html> '''


        except Exception as e:
            print(e)
            return "Something went wrong"
        
    
    return '''<form method="POST">
                Book title:<input type = "text" name = "title"> <br>
                Author:<input type = "text" name = "author"> <br>
                <input type = "submit" value = "Add Book">
                </form>
            '''


@app.route('/delete_book/<int:id>', methods=['GET', 'POST'])
def delete_book(id):
    to_be_deleted = Library.query.get(id)
    
    if to_be_deleted is None:
        return "Book not found"

    if request.method == 'GET':
        return f'''
        <form method="POST">
            <p>Are you sure you want to delete this book?</p>
            <p>Title: {to_be_deleted.title}</p>
            <p>Author: {to_be_deleted.author}</p>
            <button type="submit">Yes, Delete</button>
        </form>
        '''
    
    try:
        # Perform the delete operation
        data_base.session.delete(to_be_deleted)
        data_base.session.commit()
        wait_time = 3000
        seconds = wait_time / 1000
        redirect_url = '/all_books'

        return f'''<html><body><p>book '{to_be_deleted.title}' By '{to_be_deleted.author}' has been deleted!</p>
            You will be redirected in { seconds } seconds</p>
            <script>var timer = setTimeout(function() {{window.location='{ redirect_url }'}},
            { wait_time });</script></body></html> '''

    
    except Exception as e:
        print(e)
        return "Something went wrong"
    

@app.route('/edit_book/<int:id>', methods=['GET', 'POST'])
def edit_book(id):
    to_be_edited = Library.query.get(id)
    
    if to_be_edited is None:
        return "Record not found"
    
    if request.method == 'GET':
        return f'''
        <form method="POST">
            <p>Edit the book's details below:</p>
            <label for="title">Title:</label>
            <input type="text" name="title" value="{to_be_edited.title}" required><br>
            <label for="author">Author:</label>
            <input type="text" name="author" value="{to_be_edited.author}" required><br>
            <button type="submit">Update</button>
        </form>
        '''
    
    if request.method == 'POST':
        new_book_title = request.form.get("title")
        new_book_author = request.form.get("author")
        
        if not new_book_title or not new_book_author:
            return "Both title and author are required."
        
        wait_time = 3000
        seconds = wait_time / 1000
        redirect_url = '/all_books'
        
        try:
            # Update the book
            to_be_edited.title = new_book_title
            to_be_edited.author = new_book_author
            data_base.session.commit()

            return f'''<html><body><p>Book with ID: {id} has been updated to:</p>
            <p>Title: {new_book_title}</p>
            <p>Author: {new_book_author}</p>
            You will be redirected in {seconds} seconds.</p>
            <script>var timer = setTimeout(function() {{window.location='{redirect_url}'}},
            {wait_time});</script></body></html>'''
        
        except Exception as e:
            print(e)
            return "Something went wrong"

@app.route('/all_books')
def all_books():
    books=Library.query.order_by(Library.id).all()
    return render_template('table.html', books=books)

@app.route('/search', methods=['GET', 'POST'])
def search_book():
    if request.method == 'GET':
        return f'''
        <form method="POST">
            <label for="keyword">Search by Title or Author:</label>
            <input type="text" name="keyword" placeholder="Enter keyword">
            <label for="author">Filter by Author:</label>
            <input type="text" name="author" placeholder="Enter author name">
            <button type="submit">Search</button>
        </form>
        '''
    
    if request.method == 'POST':
               
        try:
            keyword = request.form.get("keyword")
            author = request.form.get("author")
            redirect_url = f"/search_results/{keyword or 'none'}/{author or 'none'}"

            return redirect(redirect_url)
        
        except Exception as e:
            print(e)
            return "Something went wrong"

@app.route('/search_results/<keyword>/<author>', methods=['GET', 'POST'])
def search_results(keyword, author):
    query = Library.query
    if keyword != "none":
        query = query.filter(Library.title.ilike(f"%{keyword}%"))
    
    if author!= "none":
        query = query.filter(Library.author.ilike(f"%{author}%"))
    
    books = query.all()
    if books == []:
        return f'''<html><body><p>Sorry! not found</p>
                    </body></html>'''

    else:  
        return render_template('results.html', books=books)



if __name__ == '__main__':
    app.run(debug=True)  
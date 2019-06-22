<html>
	<head><title>Query Page</title>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<style>
	body {background-color: #efefef;
    font-family: Arial, Helvetica, sans-serif;}
	* {
    box-sizing: border-box;
}
	.background{
	text-align: center;
	height: 100%;
	width: 100%;
		min-width: 1500px;
	}
	.title{
		position: absolute;
		width: 12%;
		margin: 1%;
		left: 26%;
		top: 1%;
		display: inline-block;
	}
	.searchbar{
		position: absolute;
		top: 10%;
		padding: 1.5em 0.75em;
		font-size: 15px;
		height: 5%;
		width: 20%;
		appearance: none;
		border: 100px;
		box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.2);
		background: #fff;
		border-radius: 10px;
	}
	.displayBlock{
		padding: 1em 0.75em;
		background: orange;
		float:right;
		margin-right:3%;
		margin-top: 10%;
		appearance: none;
		border: 1px solid darkgrey;
		box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.2);
		background: #fff;
		border-radius: 10px;
	}
	.loginbar{
	  position: absolute;
      top: 5%;
      right: 10%;
	  height: 5%;
	  width: 4%;
	  color: white;
	  background: orange;
	  border-radius: 6px;
	  text-align: center;
	  font-weight: 600;
	  font-size: 15px;
	  display: inline-block;
	  border: 3px
	}
	.loginbar:hover{
		background-color: #F7DC6F;
	}
	.pagination {
    	display: inline-block;
		position:absolute;
		left: 900px;
		bottom: 40px;
	}
	.pagination a {
    	color: black;
    	float: left;
    	padding: 18px 26px;
    	text-decoration: none;
	}
	.pagination a:hover:not(.active) {
    	background-color: orange;
    	border-radius: 5px;
	}
	.pagebar {
		position:absolute;
		left: 1000px;
		bottom: 70px;
	}
	.urltable{
		position: absolute;
		top: 30%;
		left: 2%;
		position: absolute;
		padding: 0.75em 0.75em;
		font-size: 15px;
		border: 1px solid darkgrey;
		box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.2);
		background: #fff;
		border-radius: 10px;
		width: 70%;
		height: 50%;
	}
	.search_result{
		position: absolute;
		left: 10%;
		top: 20%;
	}
	.Nothing_found{
		position: absolute;
		left: 10%;
		top: 40%;
	}
	.go{
		position: absolute;
		height: 5%;
		width: 4%;
		color: white;
		left: 65%;
		top: 10%;
		background: orange;
		border-radius: 5px;
		text-align: center;
		font-weight: 600;
		font-size: 20px;
		border: 3px;"
	}
	.go:hover {
		background-color: #F7DC6F;
	}
	.go:active {
	  background-color: #F7DC6F;
	}
	</style>
	</head>
	<body>
		<div>
			<div class = "background">
				<div> <a href="/"><img src="/static/switch_pokemonletsgopikachu_logo.png" class = "title"></div></a>

				<div class = "displayBlock">
					<p>Search for: "{{SearchingTerm}}"<p>
						<table id ="results" style = "text-align:center" width = "30%" height = "10%" cellspacing = "1px" >
							<tr>
								<td><b>Word <br> </b></td>
								<td><b>Count</b></td>
							</tr>
							%for term in reversed(Input):
								%word = term[0]
								%count = term[1]
								<tr>
									<td>{{word}}</td>
									<td>{{count}}</td>
								</tr>
							%end
						</table>
				</div>


					<div><form action = "/get" method = "GET">
					<input class="searchbar" name="keywords" type="text" placeholder="Search Keywords">
					<input class="go" value="Go!" type="submit">
					</form>
					</div>

					<div class = "search_result"><b>Search Result</b>
						<br><p>The correct input should be:</p>
						<a href="/get?keywords={{misspelled}}">{{misspelled}}</a>
					</div>
					%if(pagelength != 0):
						<div class = "urltable">
							<table id ="url_result" cellspacing = "30px" width = "70%" height = "10%">
								%for term in range(0,pagelength):
									%url = url_list[term]
									<tr>
										<td>{{url[1]}}<br>
										<a href={{url[0]}}>{{url[0]}}</a></td>
									</tr>
								%end
							</table>
						</div>
					%else:
					<div class = "Nothing_found">
						<p>Nothing can be found!<br>You may want to search(the most frequent page):</p>
						%if(found_like_phase != None):
							%a = ""
							%for term in found_like_phase:
								%a += term + " "
							%end
							<a href="/get?keywords={{a}}">{{a}}</a><b>?</b>
						%else:
							<p><br>please search again</p>
						%end
					</div>
					%end
						<!--<div class="pagebar"><input value= {{page_num}} type="text" name="pape_num" /></div>-->
						<div class="pagination">
							<p>Current page: {{page_num}}<p>
						 	<a href="/&keywords={{SearchingTerm}}&page={{prev_page}}"><font size = "20">&laquo;</a>
							<a href="/&keywords={{SearchingTerm}}&page={{next_page}}"><font size = "20">&raquo;</a>
						</div>
				</form>

				<form action = "/login">
				<div><input value="login" type="submit" class = "loginbar"></div>
				</form>
			</div>
		</div>
	</body>
</html>

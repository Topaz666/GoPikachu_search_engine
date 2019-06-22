<!--This is html for homepage which includes a picture, a search bar, we use get method to go to next step!-->

<html>
	<head><title>Pikachu</title></head>
	<style>
	body {background-color: #efefef;
    font-family: Arial, Helvetica, sans-serif;}
	.background{
		text-align:center;
		height:100%;
		width: 100%;
    flex-wrap: wrap;
		min-width: 1500px;
	}
    .loginbar{
      position: absolute;
      top: 5%;
      right: 10%;
	  height:36px;
	  width:70px;
	  color: white;
	  background: orange; 
	  border-radius: 6px;
	  text-align: center;
	  font-weight: 600; 
	  font-size: 15px;
	  border: 3px
	}
	.go{
	  height:40px;
      width:60px;
      color: white;
      background: orange; 
      border-radius: 8px;
      text-align: center; 
      font-weight: 600; 
      font-size: 20px;
      display: inline-block;
      border: 3px;"
	}
	.loginbar:hover{
	  background-color: #F7DC6F;
	}
	.go:hover {
	  background-color: #F7DC6F;
	}
	.loginbar:active {
	  background-color: #F7DC6F;
	}
	.go:active {
	  background-color: #F7DC6F;
	}
	.title{
		/*font-family:*/
        width: 70%;
        margin: 1%;
		display:inline-block;
	}
	.Hotrank{
 		position: absolute;
      	top: 30%;
      	left: 1%;
      	box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.2);
      	padding: 1em 0.75em;
		font-size: 10px;
	}
	.user_picture{
 		position: absolute;
      	top: 1%;
      	left: 1%;
	}
	.user_name{
 		position: absolute;
      	top: 8%;
      	left: 1%;
		text-align: left;
		color: orange;  
		font-size: 15px
	}
	.searchbar{
		/*background-color: #009000;*/
      font-size: 18px;
      padding: 1em 0.75em;
      width: 40%;
      margin: 2%;
      appearance: none;
      border: 100px;
      box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.2);
      background: #fff;
      border-radius: 10px;
			display:inline-block;
	}
	.pagination a {
    	color: black;
    	float: left;
    	padding: 18px 26px;
    	text-decoration: none;
	}
	.pagination a:hover:not(.active) {
    	background-color: #4CAF50;
    	border-radius: 5px;
	}
    .picture{
      max-width:620px;
      width:expression(document.body.clientWidth>620?"620px":"auto");
      max-height:300px;
      height:expression(document.body.clientHeight>300?"300px":"auto");
      overflow:hidden;
      margin:10 auto;
      width: 70%;
			display:inline-block;
	}
</style>
	<body>
		<div>
			<div class = "background">
				<div class = "title"> <img src="/static/switch_pokemonletsgopikachu_logo.png" height="20%" width=auto></div>
				<div class = "picture"> <img src="/static/025Pikachu-Original.png" height="20%" width=auto> </div>
				<form action = "/get" method = "GET">
				<div><input class="searchbar" name="keywords" type="text" placeholder="Search Keywords"></div>
				<input class="go" value="Go!" type="submit">
				</form>
				<form action = "/logout">
				<input value="logout"  type="submit" class ="loginbar">
				</form>
				<div class = "Hotrank">
				<h1>Top 10 Keywords Searched</h1>
						<table id ="history" style = "text-align:left;">
							<tr>
								<td><b>Word <br> </b></td>
								<td><b>Count</b></td>
							</tr>
							%for term in reversed(History):
								%word = term[0]			
								%count = term[1]
								<tr>
									<td>{{word}}</td>
									<td>{{count}}</td>
								</tr>
							%end
						</table>
				</div>
				<div class = "user_picture"><img src={{user_picture}} style ="height:60px;width:50px;border-radius: 60px;"></div>
				<div class = "user_name"><b>{{user_ID}}<br>{{user_name}}</b></div>
			</div>
		</div>
	</body>
</html>

<!--This is html for homepage which includes a picture, a search bar, we use get method to go to next step!-->

<html>
	<head><title>Pikachu</title></head>
	<style>
	body {background-color: #efefef;
    font-family: Arial, Helvetica, sans-serif;}
	.background{
		text-align: center;
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
	  display: inline-block;
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
		display: inline-block;
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
	display: inline-block;
	}
    .picture{
      max-width:620px;
      width: expression(document.body.clientWidth>620?"620px":"auto");
      max-height:300px;
      height: expression(document.body.clientHeight>300?"300px":"auto");
      overflow: hidden;
      margin:10 auto;
      width: 70%;
	display: inline-block;
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

				<form action = "/login">
				<input value="login"  type="submit" class ="loginbar">
                </div>
				</form>
			</div>
		</div>
	</body>
</html>

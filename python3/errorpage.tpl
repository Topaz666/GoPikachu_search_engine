<!--This is html for homepage which includes a picture, a search bar, we use get method to go to next step!-->

<html>
<head><title>Pikachu</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
* {
  box-sizing: border-box;
}
body {background-color: #efefef;
font-family: Arial, Helvetica, sans-serif;}

.background{
	text-align: center;
	height: 100%;
	width: 100%;
  flex-wrap:wrap;
}
.title {
	/*background-color: #004000;*/
	text-align: center;
	color: #2980B9;
	width: 70%;
	margin: 1%;
	display: inline-block;
}
	.loginbar{
		text-align: center;
		display: inline-block;
		height:30px;
		width:10%;
		color: white;
		font-weight: 600;
		font-size: 15px;
		border: 3px;
		border-radius: 8px;
		background: #3498DB;

	}
	.loginbar:hover{
		background-color: #A7DBFD;
	}
	.picture{
		max-width:620px;
		width:expression(document.body.clientWidth>620?"620px":"auto");
		max-height:300px;
		height:expression(document.body.clientHeight>300?"300px":"auto");
		overflow:hidden;
		margin:5% auto;
		width: 70%;
		display:inline-block;
}
	</style>
	<body>
		<div>
			<div class = "background">
				<div class = "picture"> <img src="/static/195.png" height="80%" width=auto> </div>
				<div class = "title"> <h1>404 SORRY, ACESS DENIED</h1> <h2>Go Back Home?</h2> </div>
				<form action = "/"

				<div> <input value="HomePage" type="submit" class = "loginbar"> </div>
				</form>

			</div>
		</div>
	</body>
</html>

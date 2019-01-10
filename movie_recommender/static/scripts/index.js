var movie_rating_dictionary = {}; //
var movie_title = ""; // For dynamically updating movie titles
var movies_list = [];
var title_to_id_map = {};
var recommendations = {}; 
var circular_queue =  [5,1,2,3,4];
var loading_animation; //To disable canvas animation when loading is finished

var typingTimer;
var doneTypingInterval = 100;


//csrf

$( window ).on("beforeunload", function(){
	$.ajax({
		url: save_ratings_url,
		type: 'HEAD',
	});
});

$(document).ready(function(){
	var csrftoken = Cookies.get('csrftoken');
	$.ajaxSetup({
		beforeSend: function(xhr, settings){
			if (!this.crossDomain){
				xhr.setRequestHeader("X-CSRFToken", csrftoken);
			}
		}
	});

	$("#movie-title-input").keyup(function(event){
		clearTimeout(typingTimer);
		typingTimer = setTimeout(getTitles, doneTypingInterval);
	});

	$("#movie-selector").children().keydown(function(event){
		clearTimeout(typingTimer);
	});

	$(".btn").mouseup(function(){
		$(this).blur();
	});
	$("#add-rating").click(validateChosenRating);
	$("#movie-title-input").autocomplete({
		source: movies_list
	});
	//$("#update-recommendations-button").click(postRatings);
	$("#update-recommendations-button").click(function(){
		if ($("#rated-movies div").length >= 1){
			$(this).unbind("click");
			$("#rating-display").switchClass("col-12","col-3", 1000);	
			$(".loading-div").animate({
				opacity:1
			}, 1000, queue=false);
		
			$(".loading-div").css("display","flex");
			postRatings();
			$(this).click(postRatings);
		}
		else{
			alert("Please rate a movie first");
		}
	});

	$("#right-img").click(selectRightImg);
	$("#left-img").click(selectLeftImg);
});

function drawLoadingAnimation(){
	var i = 0;
	var j = 0;
	var second_ripple = false;
	var lineWidth1 = 2.5;
	var lineWidth2 = 2.5;
	var lineWidthDecrement = 0.007;
	loading_animation = setInterval(function(){
		var canvas = document.getElementById("loading-canvas");
		var ctx = canvas.getContext("2d");
		ctx.clearRect(0, 0, canvas.width, canvas.height);
		drawRipple(i, ctx, canvas, lineWidth1);
		i+=0.5;
		if (second_ripple === true){
			drawRipple(j, ctx, canvas, lineWidth2);
			j+=0.5;
			lineWidth2 -= lineWidthDecrement;
		} 
		if (i > 120){
			second_ripple = true;
		}
		if (i > 240){
			i=0;
			lineWidth1 = 2.5;
		}
		if (j>240){
			j = 0;
			second_ripple = false;
			lineWidth2 = 2.5;
		}
		lineWidth1 -= lineWidthDecrement;

	}, 25);
}

function drawRipple(counter, ctx, canvas, lineWidth){
	ctx.lineWidth = lineWidth;
	ctx.beginPath();
	ctx.arc(canvas.width/2, canvas.height/2, counter, 1, 10);
	ctx.stroke()
}

function setRecommendations(){
	$("#left-img").attr("src",recommendations[circular_queue[0]][0]);
	$("#left-movie-description").text(recommendations[circular_queue[0]][1]);
	$("#left-movie-title").text(recommendations[circular_queue[0]][2]);		
	$("#left-ranking-text").text("Rank " + circular_queue[0]);

	$("#main-img").attr("src",recommendations[circular_queue[1]][0]);
	$("#main-movie-description").text(recommendations[circular_queue[1]][1]);
	$("#main-movie-title").text(recommendations[circular_queue[1]][2]);		
	$("#main-ranking-text").text("Rank " + circular_queue[1]);
	$("#imdb-link").attr("href", recommendations[circular_queue[1]][3]).text("IMDB PAGE");

	$("#right-img").attr("src",recommendations[circular_queue[2]][0]);
	$("#right-movie-title").text(recommendations[circular_queue[2]][2]);
	$("#right-movie-description").text(recommendations[circular_queue[2]][1]);		
	$("#right-ranking-text").text("Rank " + circular_queue[2]);

}

function validateChosenRating(){
	var rating_div = $("<div></div>").attr("class","row selected-ratings")
	var movie_title_given = $("#movie-title-input").val();
	if (movie_title_given in title_to_id_map){
		movie_title = movie_title_given;	
		var movie_id = title_to_id_map[movie_title];	
	}
	else{
		confirm("ERROR: This movie is not an option");
		$("#rating").val(null);
		$("#movie-title-input").val(null);
		return
	}
	var movie_rating = $("#rating").val();

	if (movie_rating == null || movie_rating == "" || parseInt(movie_rating) > 5|| parseInt (movie_rating) < 1){
		confirm("ERROR: Rating has to be from 1 to 5 and you must select a movie.");
		return;
	}
	else if (movie_id in movie_rating_dictionary && movie_rating_dictionary[movie_id] == movie_rating){
		confirm("ERROR: You already have this rating");
		return;
	}
	else if (movie_id in movie_rating_dictionary && movie_rating_dictionary[movie_id] != movie_rating){
		return;
	}

	else{
		movie_rating_dictionary[movie_id] = movie_rating;
		$("#rating").val(null);
		$("#movie-title-input").val(null);
	}

	rating_div.append(movie_title);
	rating_div.append(movie_rating);	
	addRating(movie_title, movie_rating, movie_id);
	
}

function addRating(movie_title, movie_rating, movie_id){
	var movie_title_ele = $("<span></span>").text(movie_title+": ").css('color','white').attr({"id":movie_id, "class":"rated-movie-title"});
	var rating_ele = $("<span></span>").text(movie_rating+"/5 Stars").css('color','white');
	var rating_info = $("<p></p>").append(movie_title_ele).append(rating_ele);

	var rating_info_div = $("<div></div>").append(rating_info).attr("class","ratings-div");
	var remove_rating = $("<button></button>").attr({"id":"remove-div", "class":"btn btn-dark"}).text("Remove Rating").click(function(){
		var dict_key = $(this).siblings('p:first').children('span:first').attr("id");
		delete movie_rating_dictionary[dict_key];
		$(this).parent().remove();
	});

	rating_info_div.append(remove_rating);
	$("#rated-movies").append(rating_info_div);

	$("#movie-list").val("");
	$("#rating").val(null);

}

function postRatings(){
	if (Object.keys(movie_rating_dictionary).length > 0){
		$("#recommendation-display").css('display','none');
		$(".loading-div").css("display",'flex');
		clearInterval(loading_animation);
		drawLoadingAnimation();	
		$.ajax({
			url: get_recommendations_url,
			method: "POST",
			data: movie_rating_dictionary,
			statusCode:{
				400: function(){
					alert("Cannot send an empty ratings list");
				},
				409: function(){
					alert("Please wait for current recommendations before requesting new ones");
				},
				405: function(){
					alert("This action only supports POST requests");
				}
			}

		}).done(function(data){
			$(".loading-div").css("display","none");
			$("#recommendation-display").animate({
				opacity:1
			}, 1000);
			$("#recommendation-display").css("display","flex");
			clearInterval(loading_animation);
			var counter = 1;
			for (var i in data){
				var movie_id = i
				var imdb_link = "http://www.imdb.com/title/"+movie_id+"/"
				var title = data[i][0];
				var img_url =  data[i][1];
				var description = data[i][2];
				if (description === null){
					description = "No description available";
				}
				if (img_url === null){
					img_url = empty_pic; //Most likely going have to alter this (path and the img itself)
				}

				recommendations[counter] = [img_url,description,title,imdb_link];
				counter++;
			}
			setRecommendations();
		});
	}
	else{
		alert ("Must rate at least one movie to receive a recommendations");
		return
	}
}

function getTitles(){
	var current_movie_title = $("#movie-title-input").val();
	if (current_movie_title === movie_title || current_movie_title === "" || current_movie_title in title_to_id_map){
		return;
	}
	else{
		movie_title = current_movie_title;	
		$.ajax({
			url: get_titles_url,
			method: "POST",
			data: {currently_typed:movie_title},
			statusCode:{
				400: function(){
					alert("Cannot process request without data to submit");
				},
				405: function(){
					alert("This action only supports POST requests");
				}
			}
		}).done(function(data){
			if (data === undefined){
				return
			}
			console.log("k");
			movies_list = [];
			/*
				Emptying to avoid having too many titles on users system, makes experience really slow. 
				In practice user may only load <10k movie titles so maybe worth keeping titles
			*/
			title_to_id_map = {}; 
			for (var i in data){
				movies_list.push(data[i].movie_title+" ("+data[i].year+")");
				title_to_id_map[data[i].movie_title+" ("+data[i].year+")"] = data[i].movie_id;
			}
			$("#movie-title-input").autocomplete({
				source: movies_list
			}).focus(function(){
				$(this).autocomplete("search");
			});
		});
	}
}


function selectRightImg(){
	/*
	var new_main_img_src = $(this).attr("src");
	$("#main-img").attr("src",new_main_img_src);
	$("#description-text").text()
	*/

	circular_queue.push(circular_queue.shift());

	$(".col-right img").parent().animate({
		opacity: 0,
		paddingRight:"100%"

	}, {duration: 250, queue:false, complete:function(){
		$("#right-img").attr("src",recommendations[circular_queue[2]][0]);
		$("#right-movie-title").text(recommendations[circular_queue[2]][2]);
		$("#right-movie-description").text(recommendations[circular_queue[2]][1]);		
		$("#right-ranking-text").text("Rank " + circular_queue[2]);


		$("#main-content").animate({
			opacity:0
		}, 200);

		$(this).animate({
			opacity:1,
			paddingRight:"0"
		}, {duration: 250, queue:false, complete:function(){

			$(".col-left img").parent().animate({
				opacity: 0,
				paddingRight:"100%"
			}, {duration:250, queue:false, complete:function(){
				$("#left-img").attr("src",recommendations[circular_queue[0]][0]);
				$("#left-movie-description").text(recommendations[circular_queue[0]][1]);
				$("#left-movie-title").text(recommendations[circular_queue[0]][2]);		
				$("#left-ranking-text").text("Rank " + circular_queue[0]);

				$("#main-content").animate({
					opacity:1
				}, 200);

				$(this).animate({
					opacity:1,
					paddingRight:"0"
				},{duration:250, queue:false});
			}});
				$("#main-img").attr("src",recommendations[circular_queue[1]][0]);
				$("#main-movie-description").text(recommendations[circular_queue[1]][1]);
				$("#main-movie-title").text(recommendations[circular_queue[1]][2]);		
				$("#main-ranking-text").text("Rank " + circular_queue[1]);
				$("#imdb-link").attr("href", recommendations[circular_queue[1]][3]).text("IMDB PAGE");

			
		}});
	}});




	
}


function selectLeftImg(){
	/*
	var new_main_img_src = $(this).attr("src");
	$("#main-img").attr("src",new_main_img_src);
	$("#description-text").text()
	*/
	
	circular_queue.unshift(circular_queue.pop());

	$(".col-left img").parent().animate({
		opacity: 0,
		paddingLeft:"100%"

	}, {duration: 250, queue:false, complete:function(){
		$("#left-img").attr("src",recommendations[circular_queue[0]][0]);
		$("#left-movie-description").text(recommendations[circular_queue[0]][1]);
		$("#left-movie-title").text(recommendations[circular_queue[0]][2]);
		$("#left-ranking-text").text("Rank " + circular_queue[0]);

		$("#main-content").animate({
			opacity:0
		}, 200);


		$(this).animate({
			opacity:1,
			paddingLeft:"0"
		}, {duration: 500, queue:false, complete:function(){

			$(".col-right img").parent().animate({
				opacity: 0,
				paddingLeft:"100%"
			}, {duration:250, queue:false, complete:function(){		
				$("#right-img").attr("src",recommendations[circular_queue[2]][0]);
				$("#right-movie-title").text(recommendations[circular_queue[2]][2]);
				$("#right-movie-description").text(recommendations[circular_queue[2]][1]);		
				$("#right-ranking-text").text("Rank " + circular_queue[2]);

				$(this).animate({
					opacity:1,
					paddingLeft:"0"
				},{duration:250, queue:false});
				}});

				$("#main-img").attr("src",recommendations[circular_queue[1]][0]);
				$("#main-movie-description").text(recommendations[circular_queue[1]][1]);
				$("#main-movie-title").text(recommendations[circular_queue[1]][2]);		
				$("#main-ranking-text").text("Rank " + circular_queue[1]);
				$("#imdb-link").attr("href", recommendations[circular_queue[1]][3]).text("IMDB PAGE");


				$("#main-content").animate({
					opacity:1
				}, 200);


		}});
	}});

	

}


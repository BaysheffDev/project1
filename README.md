# Project 1

This web application allows users to search for information
from a database of 5000 books which shows corresponding ratings information
from goodreads.com.

The user is able to create an account by registering and is able to log in/out for
subsequent sessions.

The user is able to search for a relevant book isbn, title, or author in home
page search bar which will return all matches containing exact or part matches
according to the users text entry.

Search results display on the books page in a single list format as well as a star
rating (score out of 5) and a text review if the user has previously submitted
these for the relevant book. The user can change these and re-submit the changes,
but can only have a single rating/review per book.

// scripts.js
This file contains scripts which alter the visual appearance of the star rating
for a book according to the rating score the user applies with the range slider
while also displaying this score above the slider.
It also allows the review textbox's display to toggle.

// book.html
This template contains jinja logic to display relevant book information as
retrieved from the database and the goodreads.com api for ratings data.
A visual star rating will also display based on the goodreads.com average rating.
The users ratings and reviews will also display in accordance with any entries
that have been made in the database.

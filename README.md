# Pythopn-5_MORE-Flask-APP
 
This read me will have a section for each route and the HTML page that corresponds to that page. 

----------Color Scheme & Design------------

    Our color scheme for the site is gold, silver and black

    Here is a list of the css Codes for the colors we are gonna be using for the site:
    
        gold: #ffd700
        silver: #c0c0c0
        black: #000000

----------------------------------------------------------------------------------------------

"/"
This will be the landing page for the app and inform the users what it is that they will get getting from the app and how the app can be used to help them meet their goals. 
---------------------------------------------------------------------------------------------------
"/login"
This is where the user will either be able to login with Oauth or email and password 
------------------------------------------------------------------------------------------------------
"/signup"
this page will be where we gather the needed information from the user and return the collected data too the database to be used at a later time
--------------------------------------------------------------------------------------------------------
"/authorized"
This will be the page that the user sees when they have successfuly complete the sign up or have completed the login verification. 
This page will show the saved lifts for the used and allow them to add lifts that they want in the future and set and adjust those numbers 
if the completed butten on each lift is pressed the lift will have 5 pounds added too it for the next session 
if the fail button is pressed then the user will have the sets and reps adjusted to make up for the lift being missed and the numbers will be kept the same for the next session 





/****************************current issues that are being worked on*************************************/
1.Oauth api key needs to be aproved and set 
2.hashing and salting for passwords on the db 
3.deployment is still an issue but the video from lecture 11 needs to be reviewed and a basic app can be deolpyed in the same manner 
4.we are not able to deploy anything to fly.io at all now even when we were able to deploy the base app before. nothing we can do about that so we are skipping deployment. This means that we cannot get a database working tho with fly and I have been trying to get a local db running but for some reason I can not connect to the local db to be able to test if anything we are working on is working. 

5.
6.
7.


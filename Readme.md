Crawler and keyword variation 

Code author
-----------
Mingming Li

Execution
------------
crawler_file_recover.ipynb should compile in Jupyter. I also prepared a .py file, but I didn't test this version yet. 

1)Call problem1() and type:
https://en.wikipedia.org/wiki/Time_zone” 
will get the file for problem1

2)After call problem1() with 
https://en.wikipedia.org/wiki/Electric_car
https://en.wikipedia.org/wiki/Carbon_footprint
-- Attention: call problem1() each time will create Frontier.log. You should change Frontier.log to:
'ElectricCar.txt', 'CarbonFootprint.txt','Timezon.txt' for problem2
-- I prepared them in the prepare data for problem2 folder. You could use them derectly 
and then call problem2()
will get the merge file “problem2result.txt” for problem2

3)Call problem3() and type:
will get the result for problem3 


5)However, the crawler works well but ineffectively. I run it for the homework in two days!
 Probably my crawler spend much time on finding the pattern or estimating the words correlation.
 For problem 3, my crawler just travels though 6 depth for more than two hours and just get less than 200 useful URLS which are good quality. 
- problem1 3 depth
- problem2 3 depth (using the result from problem1)
- problem3 6 depth

6)When you run the crawler, it will show you the execution information in log file. For
instance, you will find where it got blocked, where it can’t deprive content from the URL, and all the step details.Importantly, if the ignore pattern, such as disambiguation page, table link, external links, will record in the ignore.log. You could double check that.










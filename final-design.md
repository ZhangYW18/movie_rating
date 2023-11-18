noise:

1. movie avg rating - try our best to make it close to the true value, but blur the rating distribution. Show the rating distribution based on noised ratings.

2. user rating: have a setting that could be on/off (?). If on, for all public ratings: 

   show noised ratings with delta(-2<=delta<=2) using exponential dp rule. try our best to make user's avg noised rating close to avg true rating. 

   If not: the score of exponential dp for a specific user should be related to the ratio: (sum(noised rating) - sum(true rating))/sum(rated movies for a user)



Advance Feature:

User could set the range of noise(delta).



evaluation: calculate the variance of score distribution for movies.





API List (TODO):

- Evaluate   
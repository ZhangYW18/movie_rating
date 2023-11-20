noise:

1. movie avg rating - try our best to make it close to the true value, but blur the rating distribution. Show the rating distribution based on noised ratings.

   - special case: when a movie's rating is almost highest/lowest, we can hardly add noise to its ratings - makes sense because almost every one gives a full score or lowest score, and in this case it's unnecessary to add any noise.

2. user rating: have a setting that could be on/off (?). If on, for all public ratings: 

   show noised ratings with delta(-2<=delta<=2) using exponential dp rule. try our best to make user's avg noised rating close to avg true rating. 

   If not: the score of exponential dp for a specific user should be related to the avg_noise of a user's all rated movies



Advance Feature:

User could set the range of noise(delta).



evaluation: calculate the variance of score distribution for movies.





API List (TODO):

- Evaluate   
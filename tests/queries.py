# Account queries
create_user = """
mutation createUser(
    $email: String!,
    $username: String!,
    $password1: String!,
    $password2: String!
    ) {
  register(
    email:$email,
    username: $username,
    password1: $password1,
    password2: $password2) {
      success
      token
      errors
  }
}
"""

last_user = """query {
  users (last: 1){
    edges {
      node {
        id,
        uid,
        username,
        email,
      }
    }
  }
}
"""

list_users = """
query {
  users {
    edges {
      node {
        uid
        username
        email
        isActive
        verified
      }
    }
  }
}
"""

list_users_by_email = """
query ($email: String!){
  users(email: $email){
    edges {
      node {
        uid
        username
        isActive
        verified
      }
    }
  }
}

"""

# Profile queries

my_profile = """query {
   myProfile {
    email
    username
    followersCount
    tweets {
      created
      content
    }
    retweets {
      likes
      tweet {
        uid
      }
    }
    comments {
      content
    }
    likes {
      __typename
      ... on BaseDatedType {
        uid
      }
    }
  }
}"""

my_followers = """query myFollowers(
    $first: Int,
    $skip: Int
) {
  myProfile {
    followers(first: $first, skip: $skip) {
      uid
      email
      username
    }
  }
}"""

my_subs = """query mySubs(
    $first: Int,
    $skip: Int
) {
  myProfile {
    follows(first: $first, skip: $skip) {
      uid
      email
    }
  }
}"""

user_profile = """query userProfile(
    $uid: String!
) {
  userProfile(uid: $uid) {
    uid
    email
    username
    followersCount
    tweets {
      created
      content
    }
  }
}"""

user_followers = """query userFollowers(
    $uid: String!
) {
  userProfile(uid: $uid) {
    followers {
      uid
      email
    }
  }
}"""

user_subs = """query userSubs(
    $uid: String!
) {
  userProfile(uid: $uid) {
    follows {
      uid
      email
    }
  }
}
"""


# Tweet queries
create_tweet = """mutation newTweet(
    $content: String!
){
  createTweet(content: $content){
    tweet {
      content
      likes
      comments
      retweets
      created
    }
  }
}"""

create_retweet = """mutation createRetweet(
    $tweetUid: String!
) {
  createRetweet(tweetUid: $tweetUid){
    retweet {
      uid
      likes
      comments
      created
      tweet {
        uid
        content
        likes
        comments
        retweets
      }
    }
  }
}"""

like = """mutation createLike(
    $uid: String!,
    $type: String!,
) {
  like(uid: $uid, type: $type){
      __typename
    ... on BaseDatedType {
      uid
    }
      likes
    ... on TweetType{
      content
    }
    ... on ReTweetType {
      comments
    }
    ... on CommentType {
      content
    }
  }
}"""

unlike = """mutation DeleteLike(
  $uid: String!,
  $type: String!
) {
  unlike(type: $type, uid: $uid){
    __typename
    ... on BaseDatedType {
        uid
      }
    ... on LikeableType {
      likes
    }
  }
}
"""

create_comment = """mutation createComment(
    $uid: String!,
    $type: String!
    $content: String!,
) {
  createComment(uid: $uid, type: $type, content: $content){
    commentable {
      __typename
      comments
      commentsList {
        content
        created
      }
      ... on TweetType {
        uid
        likes
      	content
      }
      ... on ReTweetType {
        uid
        likes
        tweet {
          content
        }
      }
    }
  }
}"""

follow_user = """mutation followUser(
  $uid: String!
) {
  followUser(uid: $uid){
    user {
      uid
      email
      username
      followersCount
    }
  }
}"""

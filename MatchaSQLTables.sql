USE master
GO

IF EXISTS(select * from sys.databases where name='MatchaDB')
DROP DATABASE MatchaDB

CREATE DATABASE MatchaDB;
GO

USE MatchaDB;
GO

CREATE TABLE [dbo].[Users](
	[UserID] [int] IDENTITY(1,1) NOT NULL,
	[Username] [varchar](120) NOT NULL,
	[Password] [varchar](130) NOT NULL,
	[FirstName] [varchar] (120) NOT NULL,
	[LastName] [varchar] (120) NOT NULL,
	[Email] [varchar](50) NOT NULL,
	[Age] [int] NOT NULL,
	[Gender] [int] DEFAULT 2,
	[Sexuality] [tinyint] DEFAULT 2,
	[Location] [geography],
	[Bio] [varchar] (500),
	[Fame] [int] DEFAULT 0,
	[LastLogin] [datetime] DEFAULT GETDATE(),
	--Chat/Likes/Matches go in different table because multiple

	CONSTRAINT [PK_Users] PRIMARY KEY CLUSTERED ([UserID] ASC),
	CONSTRAINT [AK_Username_Email_Unique] UNIQUE(Username, Email)
);
GO

CREATE TABLE [dbo].[Likes](
	[LikeID] [int] IDENTITY(1,1) NOT NULL,
	[ThingLiked] [varchar](100) NOT NULL,

	CONSTRAINT [PK_Likes] PRIMARY KEY CLUSTERED ([LikeID] ASC),
);
GO

CREATE TABLE [dbo].[UserLikes](
	[UserID] [int] NOT NULL,
	[LikeID] [int] NOT NULL,

	CONSTRAINT [PK_Cluster_Users] PRIMARY KEY CLUSTERED ([UserID], [LikeID] ASC),
	CONSTRAINT [AK_User_Likes_Unique] UNIQUE ([LikeID],[UserID]),
	CONSTRAINT [FK_LikedThing] FOREIGN KEY([LikeID])
		REFERENCES [dbo].[Likes] ([LikeID]),
	CONSTRAINT [FK_UserLiking] FOREIGN KEY([UserID])
		REFERENCES [dbo].[Users] ([UserID]) ON DELETE CASCADE
);
GO

CREATE TABLE [dbo].[Posts](
	[PostID] [int] IDENTITY(1,1) NOT NULL,
	[UserID] [int] NOT NULL,
	[Image] [varbinary](MAX) NOT NULL,
	[Description] [varchar](250),

	CONSTRAINT [PK_Posts] PRIMARY KEY CLUSTERED ([PostID] ASC),
	CONSTRAINT [FK_UserPosting] FOREIGN KEY([UserID])
		REFERENCES [dbo].[Users] ([UserID]) ON DELETE CASCADE
);
GO

CREATE TABLE [dbo].[Chatlogs] (
	[LogID] [int] IDENTITY(1,1) NOT NULL,
	[UserSenderID] [int] NOT NULL,
	[UserReceiverID] [int] NOT NULL, -- make chatrooms users
	[SentTime] [DATETIME] DEFAULT GETDATE(),
	[Message] [varchar](250) NOT NULL,

	CONSTRAINT [PK_Logs] PRIMARY KEY CLUSTERED ([LogID] ASC),
	CONSTRAINT [FK_UserSenderID] FOREIGN KEY ([UserSenderID])
		REFERENCES [dbo].[Users] ([UserID]),
	CONSTRAINT [FK_UserReceiverID] FOREIGN KEY ([UserReceiverID])
		REFERENCES [dbo].[Users] ([UserID]),
)
CREATE TABLE [dbo].[Matches] (
	[MatchID] [int] IDENTITY(1,1) NOT NULL,
	[UserOneID] [int] NOT NULL,
	[UserTwoID] [int] NOT NULL,
	[Onelikes] [binary] DEFAULT 0,
	[Twolikes] [binary] DEFAULT 0,

	CONSTRAINT [PK_Matches] PRIMARY KEY CLUSTERED ([MatchID] ASC),
	CONSTRAINT [FK_UserOneID] FOREIGN KEY ([UserOneID])
		REFERENCES [dbo].[Users] ([UserID]) ON DELETE CASCADE,
	CONSTRAINT [FK_UserTwoID] FOREIGN KEY ([UserTwoID])
		REFERENCES [dbo].[Users] ([UserID]),
)
from googleapiclient.discovery import build
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
api_key ='AIzaSyCSJ1borZjWaW3E22WU0qM2XR1O0YVRWyw'
channel_id = 'UCuAXFkgsw1L7xaCfnd5JJOw'
youtbe = build('youtube', 'v3', developerKey=api_key)
## function to get channel statistics
def get_channel_stats(youtbe, channel_id):
    request = youtbe.channels().list(
        part='snippet,contentDetails,statistics',
        id=channel_id
    )
    response = request.execute()
    data = dict()
    for item in response['items']:
        data['channel_name'] = item['snippet']['title']
        data['subscribers'] = item['statistics']['subscriberCount']
        data['views'] = item['statistics']['viewCount']
        data['total_videos'] = item['statistics']['videoCount']
        data['playlist_id'] = item['contentDetails']['relatedPlaylists']['uploads']
    return data
channel_stats = get_channel_stats(youtbe, channel_id)
playlist_id = channel_stats['playlist_id']
## function to get video ids
def get_video_ids(youtbe, playlist_id):
    video_ids = []
    request = youtbe.playlistItems().list(
        part='contentDetails',
        playlistId=playlist_id,
        maxResults=50
    )
    response = request.execute()
    for item in response['items']:
        video_ids.append(item['contentDetails']['videoId'])
    next_page_token = response.get('nextPageToken')
    while next_page_token:
        request = youtbe.playlistItems().list(
            part='contentDetails',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token   
        )
        response = request.execute()
        for item in response['items']:
            video_ids.append(item['contentDetails']['videoId'])
        next_page_token = response.get('nextPageToken')
    return video_ids
video_ids = get_video_ids(youtbe, playlist_id)
## function to get video details
def get_video_details(youtbe, video_ids):       
    all_video_info = []
    for i in range(0, len(video_ids), 50):
        request = youtbe.videos().list(
            part='snippet,statistics,contentDetails',
            id=','.join(video_ids[i:i+50])
        )
        response = request.execute()
        for video in response['items']:
            video_info = dict()
            video_info['video_id'] = video['id']
            video_info['title'] = video['snippet']['title']
            video_info['published_date'] = video['snippet']['publishedAt']
            video_info['views'] = video['statistics'].get('viewCount', 0)
            video_info['likes'] = video['statistics'].get('likeCount', 0)
            video_info['comments'] = video['statistics'].get('commentCount', 0)
            video_info['duration'] = video['contentDetails']['duration']
            all_video_info.append(video_info)
    return all_video_info
video_details = get_video_details(youtbe, video_ids)
## creating dataframe
video_data = pd.DataFrame(video_details)
video_data['views'] = pd.to_numeric(video_data['views'])
video_data['likes'] = pd.to_numeric(video_data['likes'])
video_data['comments'] = pd.to_numeric(video_data['comments'])
video_data['published_date'] = pd.to_datetime(video_data['published_date'])
print(video_data.head())
# Correlation analysis
correlation_matrix = video_data[['views', 'likes', 'comments']].corr()
print("Correlation Matrix:")
print(correlation_matrix)
# Visualization
sns.pairplot(video_data[['views', 'likes', 'comments']])
plt.suptitle('Pairplot of Views, Likes, and Comments', y=1.02)
plt.show()
# Heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Correlation Heatmap')
plt.show()
# Save the dataframe to a CSV file
video_data.to_csv('youtube_channel_data.csv', index=False)
print("Data saved to youtube_channel_data.csv")     
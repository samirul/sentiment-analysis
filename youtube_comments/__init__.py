"""
    Will execute before fetching youtube comments
"""

from collections import deque

queue = deque()
# Not necessary but for safe side to make sure deque is clean before executing another queue/deque
while queue:
    queue.popleft()

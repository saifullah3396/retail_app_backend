"""
Defines message processors for performing custom operations on live streamed
data received from the deepstream servers connected to server.
"""

from channels.layers import get_channel_layer


class DeepstreamMessageProcessor:
    """
    Defines the base class for processing live data messages received from
    deepstream
    """

    def __init__(self, group_id):
        self.group_id = group_id

    async def __call__(self, msg):
        raise NotImplementedError()


class DeepstreamFrontendStreamerCallbackInterface(DeepstreamMessageProcessor):
    """
    Sends the messages to the local channels group so that it can be accessed
    by other parts of the django application
    """

    async def __call__(self, message):
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            self.group_id,
            {
                'type': 'deepstream_message_update',
                'message': message
            }
        )


# class DeepstreamLiveHeatMapGenerator(DeepstreamMessageProcessor):
#     """
#     Processes the messages in real-time to generate heatmaps and saves them
#     in the database.
#     """

#     def __init__(self, topic, data_process_size=200):
#         super().__init__(topic)
#         self.num_bins = 100
#         self.range_x = (0, 44.577)
#         self.range_y = (44.577, 35.2806)
#         self.data_points_x = []
#         self.data_points_y = []
#         self.data_process_size = data_process_size
#         self.xedges, self.yedges = \
#             np.linspace(*range_x, self.num_bins), \
#             np.linspace(*range_y, self.num_bins)
#         self.hist2d = None

#     async def __call__(self, msg):
#         if 'objects' in msg:
#             for obj in msg['objects']:
#                 self.data_points_x.append(
#                     obj['coordinates']['x'])
#                 self.data_points_y.append(
#                     obj['coordinates']['y'])

#             print(len(self.data_points_x))
#             if len(self.data_points_x) >= self.data_process_size:
#                 if self.hist2d is None:
#                     print("making new hist")
#                     self.hist2d, self.xedges, self.yedges = np.histogram2d(
#                         self.data_points_x,
#                         self.data_points_y,
#                         (self.xedges, self.yedges))
#                 else:
#                     print("updating old hist")
#                     self.hist2d += np.histogram2d(
#                         self.data_points_x,
#                         self.data_points_y,
#                         (self.xedges, self.yedges))[0]
#                     print(self.hist2d)

#                 extent = [self.xedges[0], self.xedges[-1],
#                           self.yedges[0], self.yedges[-1]]
#                 gaussian = gaussian_filter(self.hist2d.T, sigma=1)
#                 plt.plot(self.data_points_x,
#                          self.data_points_y, 'k.', markersize=5)
#                 # plt.clf()
#                 plt.imshow(gaussian, extent=extent,
#                            origin='lower', cmap=plt.cm.jet)
#                 plt.show()

#                 self.data_points_x = []
#                 self.data_points_y = []

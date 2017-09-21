import os

from maya import cmds

import avalon.maya
import colorbleed.api
from colorbleed.maya.lib import extract_alembic


class ExtractColorbleedPointcache(colorbleed.api.Extractor):
    """Produce an alembic of just point positions and normals.

    Positions and normals are preserved, but nothing more,
    for plain and predictable point caches.

    """

    label = "Extract Pointcache"
    hosts = ["maya"]
    families = ["colorbleed.pointcache"]

    def process(self, instance):

        nodes = instance[:]

        # Collect the start and end including handles
        start = instance.data["startFrame"]
        end = instance.data["endFrame"]
        handles = instance.data.get("handles", 0)
        if handles:
            start -= handles
            end += handles

        self.log.info("Extracting animation..")
        dirname = self.staging_dir(instance)

        self.log.info("nodes: %s" % str(nodes))

        parent_dir = self.staging_dir(instance)
        filename = "{name}.abc".format(**instance.data)
        path = os.path.join(parent_dir, filename)

        with avalon.maya.suspended_refresh():
            with avalon.maya.maintained_selection():
                cmds.select(nodes, noExpand=True)
                extract_alembic(file=path,
                                startFrame=start,
                                endFrame=end,
                                **{"step": instance.data.get("step", 1.0),
                                   "attr": ["cbId"],
                                   "writeVisibility": True,
                                   "writeCreases": True,
                                   "uvWrite": True,
                                   "selection": True})

        if "files" not in instance.data:
            instance.data["files"] = list()

        instance.data["files"].append(filename)

        self.log.info("Extracted {} to {}".format(instance, dirname))
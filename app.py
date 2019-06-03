# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import tank

class StgkStarterApp(tank.platform.Application):
    
    """
    The app entry point. This class is responsible for intializing and tearing down
    the application, handle menu registration etc.
    """
    
    def init_app(self):
        """
        Called as the application is being initialized
        """
        
        # first, we use the special import_module command to access the app module
        # that resides inside the python folder in the app. This is where the actual UI
        # and business logic of the app is kept. By using the import_module command,
        # toolkit's code reload mechanism will work properly.
        app_payload = self.import_module("app")
        menu_callback = lambda : app_payload.dialog.show_dialog(self)
        
        

        if self.context.step:
            #if "ayou" in self.context.step["name"] :
            self.engine.register_command("Set Camera", menu_callback)
       
        else:
            self.engine.register_command("Set Camera", menu_callback)

        

//
//  AppDelegate.swift
//  WhatDoIDo
//
//  Created by CSSE Department on 9/24/14.
//  Copyright (c) 2014 PaJamaKinG. All rights reserved.
//

import Foundation
import UIKit
import CoreLocation

@UIApplicationMain
class AppDelegate: UIResponder, UIApplicationDelegate {

    var window: UIWindow?
    
    var user: UserModel!
    var suggestionModel: SuggestionModel!
    var locationManager: CLLocationManager!

    func application(application: UIApplication, didFinishLaunchingWithOptions launchOptions: [NSObject: AnyObject]?) -> Bool {
        // Override point for customization after application launch.
        self.user = UserModel()
        self.suggestionModel = SuggestionModel()
        return true
    }

    func applicationWillResignActive(application: UIApplication) {
        // Sent when the application is about to move from active to inactive state. This can occur for certain types of temporary interruptions (such as an incoming phone call or SMS message) or when the user quits the application and it begins the transition to the background state.
        // Use this method to pause ongoing tasks, disable timers, and throttle down OpenGL ES frame rates. Games should use this method to pause the game.
    }

    func applicationDidEnterBackground(application: UIApplication) {
        // Use this method to release shared resources, save user data, invalidate timers, and store enough application state information to restore your application to its current state in case it is terminated later.
        // If your application supports background execution, this method is called instead of applicationWillTerminate: when the user quits.
    }

    func applicationWillEnterForeground(application: UIApplication) {
        // Called as part of the transition from the background to the inactive state; here you can undo many of the changes made on entering the background.
    }

    func applicationDidBecomeActive(application: UIApplication) {
        // Restart any tasks that were paused (or not yet started) while the application was inactive. If the application was previously in the background, optionally refresh the user interface.
    }

    func applicationWillTerminate(application: UIApplication) {
        // Called when the application is about to terminate. Save data if appropriate. See also applicationDidEnterBackground:.
    }

    func createSuggestionModelFromJSON(json: NSDictionary) -> SuggestionModel {
        // Use the JSON passed back from the suggestions call to create a Suggestion Model.
        println(json)
        var sug = SuggestionModel()
        sug.name = json["title"] as String
        sug.description = json["description"] as String
        sug.location = json["location"] as String
        sug.startTime = json["time"] as String
        return sug
    }
    
}


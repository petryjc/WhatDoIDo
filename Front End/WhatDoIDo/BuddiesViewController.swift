//
//  BuddiesViewController.swift
//  WhatDoIDo
//
//  Created by CSSE Department on 9/24/14.
//  Copyright (c) 2014 PaJamaKinG. All rights reserved.
//

import Foundation
import UIKit

class BuddiesViewController: UIViewController, UITableViewDelegate, UITableViewDataSource {
    
    @IBOutlet var addBuddyField : UITextField!
    @IBOutlet var addBuddyButton : UIButton!
    @IBOutlet var buddiesTableView : UITableView!
    
    var buddies = ["Bill", "John"] //Hold the usernames of your buddies
    var pendingBuddies = [[1, "Fred"], [2, "Jeff"]]
    var del = UIApplication.sharedApplication().delegate as AppDelegate
    
    override func viewDidLoad() {
        println("meow")
        self.buddiesTableView.registerClass(UITableViewCell.self, forCellReuseIdentifier: "cell")
        populateBuddies(["token": self.del.user.getLoginToken()]) { (succeeded: Bool, msg: String) -> () in
            println(succeeded, msg)
            // Move to the UI thread
            dispatch_async(dispatch_get_main_queue(), { () -> Void in
            })
        }
        println("ruff")
        super.viewDidLoad()
        // Do any additional setup after loading the view, typically from a nib.
    }
    
    func refreshUI() {
        self.addBuddyField.text = ""
        println("Refresh")
        println(self.buddies)
        self.buddiesTableView.reloadData()
    }
    
    func populateBuddies(params : Dictionary<String, AnyObject>, postCompleted : (succeeded: Bool, msg: String) -> ()) {
        var request = NSMutableURLRequest(URL: NSURL(string: "http://whatdoido.csse.rose-hulman.edu/api/buddy/list")!)
        var session = NSURLSession.sharedSession()
        request.HTTPMethod = "POST"
        
        var err: NSError?
        request.HTTPBody = NSJSONSerialization.dataWithJSONObject(params, options: nil, error: &err)
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        request.addValue("application/json", forHTTPHeaderField: "Accept")
        
        var task = session.dataTaskWithRequest(request) {data, response, error -> Void in
            var strData = NSString(data: data, encoding: NSUTF8StringEncoding)
            var err: NSError?
            var json = NSJSONSerialization.JSONObjectWithData(data, options: .MutableLeaves, error: &err) as? NSDictionary
            
            var msg = "No message"
            
            // Did the JSONObjectWithData constructor return an error? If so, log the error to the console
            if(err != nil) {
                println(err!.localizedDescription)
                let jsonStr = NSString(data: data, encoding: NSUTF8StringEncoding)
                println("Error could not parse JSON: '\(jsonStr)'")
                self.buddies = ["Fred", "Joe", "Gabe", "Jack", "Ben", "Kenny"]
                self.refreshUI()
                println(self.buddies)
                postCompleted(succeeded: false, msg: "Something went wrong, try again")
            }
            else {
                // The JSONObjectWithData constructor didn't return an error. But, we should still
                // check and make sure that json has a value using optional binding.
                if let parseJSON = json {
                    println(parseJSON)
                    // Okay, the parsedJSON is here, let's get the value for 'status' out of it
                    if let status = parseJSON["status"] as? NSDictionary {
                        println("Succes: \(status)")
                        var code = status["code"] as Int
                        var success = code == 0
                        if (success) {
                            println("Got buddies")
                            self.parseBuddies(parseJSON)
                            postCompleted(succeeded: success, msg: "Logged in.")
                        } else {
                            println("Didn't get buddies")
                            postCompleted(succeeded: success, msg: status["msg"] as String)
                        }
                    }
                    return
                }
                else {
                    // Woa, okay the json object was nil, something went worng. Maybe the server isn't running?
                    let jsonStr = NSString(data: data, encoding: NSUTF8StringEncoding)
                    println("Error could not parse JSON: \(jsonStr)")
                    postCompleted(succeeded: false, msg: "The server appears to be down")
                }
            }
        }
        
        task.resume()
    }
    
    func parseBuddies(buddies: NSDictionary) {
        println("----------------")
        println(buddies)
        println("----------------")
        self.refreshUI()
    }
    
    @IBAction func sendBuddyRequest() {
        sendBuddyReq(["token": self.del.user.getLoginToken(), "buddy": self.addBuddyField.text]) { (succeeded: Bool, msg: String) -> () in
            println(succeeded, msg)
            // Move to the UI thread
            dispatch_async(dispatch_get_main_queue(), { () -> Void in
            })
        }
    }
    
    func sendBuddyReq(params : Dictionary<String, AnyObject>, postCompleted : (succeeded: Bool, msg: String) -> ()) {
        if (self.addBuddyField.text != "") {
        var request = NSMutableURLRequest(URL: NSURL(string: "http://whatdoido.csse.rose-hulman.edu/api/buddy/request")!)
        var session = NSURLSession.sharedSession()
        request.HTTPMethod = "POST"
        
        var err: NSError?
        request.HTTPBody = NSJSONSerialization.dataWithJSONObject(params, options: nil, error: &err)
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        request.addValue("application/json", forHTTPHeaderField: "Accept")
        
        var task = session.dataTaskWithRequest(request) {data, response, error -> Void in
            var strData = NSString(data: data, encoding: NSUTF8StringEncoding)
            var err: NSError?
            var json = NSJSONSerialization.JSONObjectWithData(data, options: .MutableLeaves, error: &err) as? NSDictionary
            
            var msg = "No message"
            
            // Did the JSONObjectWithData constructor return an error? If so, log the error to the console
            if(err != nil) {
                println(err!.localizedDescription)
                let jsonStr = NSString(data: data, encoding: NSUTF8StringEncoding)
                println("Error could not parse JSON: '\(jsonStr)'")
                postCompleted(succeeded: false, msg: "Something went wrong, try again")
            }
            else {
                // The JSONObjectWithData constructor didn't return an error. But, we should still
                // check and make sure that json has a value using optional binding.
                if let parseJSON = json {
                    println(parseJSON)
                    // Okay, the parsedJSON is here, let's get the value for 'status' out of it
                    if let status = parseJSON["status"] as? NSDictionary {
                        println("Succes: \(status)")
                        var code = status["code"] as Int
                        var success = code == 0
                        if (success) {
                            //self.addBuddyField.text
                            postCompleted(succeeded: success, msg: "Buddy request sent")
                        } else {
                            println("Buddy request failed")
                            postCompleted(succeeded: success, msg: status["msg"] as String)
                        }
                    }
                    return
                }
                else {
                    // Woa, okay the json object was nil, something went worng. Maybe the server isn't running?
                    let jsonStr = NSString(data: data, encoding: NSUTF8StringEncoding)
                    println("Error could not parse JSON: \(jsonStr)")
                    postCompleted(succeeded: false, msg: "The server appears to be down")
                }
            }
        }
        
        task.resume()
        } else {
            println(self.buddies)
        }
    }
    
    
    func tableView(buddiesTableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        //println(self.del.user.suggestionList.count);
        //self.del.user.suggestionList.count;
        return self.buddies.count + self.pendingBuddies.count //The number of users to display
    }
    
    func tableView(buddiesTableView: UITableView, cellForRowAtIndexPath indexPath: NSIndexPath) -> UITableViewCell {
        var cell:UITableViewCell = self.buddiesTableView!.dequeueReusableCellWithIdentifier("cell") as UITableViewCell
        if (indexPath.row < self.pendingBuddies.count) {
            cell.textLabel.text = self.pendingBuddies[indexPath.row][1] as NSString
        } else {
            cell.textLabel.text = self.buddies[indexPath.row - self.pendingBuddies.count]
        }
        
        return cell
    }
    
    func tableView(buddiesTableView: UITableView!, didSelectRowAtIndexPath indexPath: NSIndexPath!) {
        //println(self.del.user.suggestionList[indexPath.row]) //Actually do something with a selected suggestion here
        //var sugg: SuggestionModel = self.del.user.suggestionList[indexPath.row]
        //Maybe pop up a confirmation window UIAlertView
        if (indexPath.row < self.pendingBuddies.count) {
            println("Accept buddy request")
            acceptReq(["token": self.del.user.getLoginToken(), "buddy_id": self.pendingBuddies[indexPath.row][0]]) { (succeeded: Bool, msg: String) -> () in
                println(succeeded, msg)
                // Move to the UI thread
                dispatch_async(dispatch_get_main_queue(), { () -> Void in
                })
            }
        }
    }
    
    func acceptReq(params : Dictionary<String, AnyObject>, postCompleted : (succeeded: Bool, msg: String) -> ()) {
        if (self.addBuddyField.text != "") {
            var request = NSMutableURLRequest(URL: NSURL(string: "http://whatdoido.csse.rose-hulman.edu/api/buddy/accept")!)
            var session = NSURLSession.sharedSession()
            request.HTTPMethod = "POST"
            
            var err: NSError?
            request.HTTPBody = NSJSONSerialization.dataWithJSONObject(params, options: nil, error: &err)
            request.addValue("application/json", forHTTPHeaderField: "Content-Type")
            request.addValue("application/json", forHTTPHeaderField: "Accept")
            
            var task = session.dataTaskWithRequest(request) {data, response, error -> Void in
                var strData = NSString(data: data, encoding: NSUTF8StringEncoding)
                var err: NSError?
                var json = NSJSONSerialization.JSONObjectWithData(data, options: .MutableLeaves, error: &err) as? NSDictionary
                
                var msg = "No message"
                
                // Did the JSONObjectWithData constructor return an error? If so, log the error to the console
                if(err != nil) {
                    println(err!.localizedDescription)
                    let jsonStr = NSString(data: data, encoding: NSUTF8StringEncoding)
                    println("Error could not parse JSON: '\(jsonStr)'")
                    postCompleted(succeeded: false, msg: "Something went wrong, try again")
                }
                else {
                    // The JSONObjectWithData constructor didn't return an error. But, we should still
                    // check and make sure that json has a value using optional binding.
                    if let parseJSON = json {
                        println(parseJSON)
                        // Okay, the parsedJSON is here, let's get the value for 'status' out of it
                        if let status = parseJSON["status"] as? NSDictionary {
                            println("Succes: \(status)")
                            var code = status["code"] as Int
                            var success = code == 0
                            if (success) {
                                //self.addBuddyField.text
                                println("Buddy request accepted")
                                postCompleted(succeeded: success, msg: "Buddy request accepted")
                            } else {
                                println("Buddy request failed")
                                postCompleted(succeeded: success, msg: status["msg"] as String)
                            }
                        }
                        return
                    }
                    else {
                        // Woa, okay the json object was nil, something went worng. Maybe the server isn't running?
                        let jsonStr = NSString(data: data, encoding: NSUTF8StringEncoding)
                        println("Error could not parse JSON: \(jsonStr)")
                        postCompleted(succeeded: false, msg: "The server appears to be down")
                    }
                }
            }
            
            task.resume()
        } else {
            println(self.buddies)
        }
    }

    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }


}


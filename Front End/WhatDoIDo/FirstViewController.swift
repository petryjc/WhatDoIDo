//
//  FirstViewController.swift
//  WhatDoIDo
//
//  Created by CSSE Department on 9/24/14.
//  Copyright (c) 2014 PaJamaKinG. All rights reserved.
//

import Foundation
import UIKit
import CoreLocation

class FirstViewController: UIViewController, UITableViewDelegate, UITableViewDataSource, CLLocationManagerDelegate {

    @IBOutlet var uNameLabel : UILabel!
    //@IBOutlet var refreshButton : UIButton!
    @IBOutlet var suggestionTableView : UITableView!
    //@IBOutlet var suggestButton : UIButton!
    @IBOutlet var suggestButton : UIButton!
    @IBOutlet var singleSuggestion : UILabel!
    
    var locationManager = CLLocationManager()
    
    var del = UIApplication.sharedApplication().delegate as AppDelegate
    var loadedName: String!
    
    @IBAction func refresh() {
        if (self.singleSuggestion != nil) {
            if (self.singleSuggestion.text == "Watch a movie.") {
                self.singleSuggestion.text = "Read a book."
            } else if (self.singleSuggestion.text == "Read a book.") {
                self.singleSuggestion.text = "Go to a concert in town."
            } else {
                self.singleSuggestion.text = "Watch a movie."
            }
        }
        self.refreshUI()
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        //uNameLabel = UILabel(frame: CGRectMake(0, 0, 200, 21))
        //self.del.user.suggestionList = []
        // Do any additional setup after loading the view, typically from a nib.
        self.suggestionTableView.registerClass(UITableViewCell.self, forCellReuseIdentifier: "cell")
        locationManager.delegate = self
        locationManager.desiredAccuracy = kCLLocationAccuracyBest
        locationManager.distanceFilter = 250
        locationManager.requestAlwaysAuthorization()
        locationManager.startUpdatingLocation()
        del.locationManager = locationManager
        getTodaysSuggestions() {
            self.refreshUI()
        }
    }
    
    func tableView(suggestionTableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        //println(self.del.user.suggestionList.count);
        return self.del.user.suggestionList.count;
    }
    
    func tableView(suggestionTableView: UITableView, cellForRowAtIndexPath indexPath: NSIndexPath) -> UITableViewCell {
        var cell:UITableViewCell = self.suggestionTableView.dequeueReusableCellWithIdentifier("cell") as UITableViewCell
        
        //var cell = UITableViewCell(style: UITableViewCellStyle.Value2, reuseIdentifier: nil);
        
        var name = self.del.user.suggestionList[indexPath.row].getName()
        var time = self.del.user.suggestionList[indexPath.row].getStartTime()
        var nsTime = time as NSString
        cell.textLabel.text = nsTime.substringWithRange(NSRange(location: 11, length: 5)) + " - " + name
        return cell
    }
    
    func tableView(suggestionTableView: UITableView!, didSelectRowAtIndexPath indexPath: NSIndexPath!) {
        //println(self.del.user.suggestionList[indexPath.row]) //Actually do something with a selected suggestion here
        var sugg: SuggestionModel = self.del.user.suggestionList[indexPath.row]
        del.suggestionModel = sugg
        println(sugg.getName())
        println(sugg.getDesc())
        println(sugg.getRoute())
        performSegueWithIdentifier("suggestionSegue", sender: self);
    }
    
    func getTodaysSuggestions(refreshUI: (() -> Void)!) {
        del.user.todaysSuggestions() { (succeeded: Bool, msg: String, suggestions: [SuggestionModel]?) -> () in
            if (succeeded) {
                println(suggestions)
                self.del.user.suggestionList = suggestions!
            } else {
        
            }
            dispatch_async(dispatch_get_main_queue(), { () -> Void in
                refreshUI()
            })
        }
    }
    
    /*func getSuggestion(refreshUI: (() -> Void)!) {
        del.user.suggest(["token": self.del.user.getLoginToken()]) { (succeeded: Bool, msg: String, json: NSDictionary?) -> () in
            var alert = UIAlertView(title: "Success!", message: msg, delegate: nil, cancelButtonTitle: "Okay.")
            if(succeeded) {
                self.del.user.suggestionList = [self.del.createSuggestionModelFromJSON(json!)]
                alert.title = "Success!"
                alert.message = msg
            }
            else {
                self.del.user.suggestionList = [self.del.createSuggestionModelFromJSON(json!)]
                alert.title = "Failed"
                alert.message = msg
            }
            // Move to the UI thread
            dispatch_async(dispatch_get_main_queue(), { () -> Void in
                // Show the alert
                //alert.show()
                refreshUI()
            })
        }
    }*/
    
    func locationManager(manager:CLLocationManager, didUpdateLocations locations:[AnyObject]) {
        println("location = \(locations)")
        var locationArray = locations as NSArray
        var locationObj = locationArray.lastObject as CLLocation
        var coord = locationObj.coordinate
        
        println(coord.latitude)
        println(coord.longitude)
        
        postLocation(["latitude": coord.latitude, "longitude": coord.longitude, "token": del.user.getLoginToken()]) { (succeeded: Bool, msg: String) -> () in
            println(succeeded, msg)
            // Move to the UI thread
            dispatch_async(dispatch_get_main_queue(), { () -> Void in
            })
            
        }
    }
    
    func locationManager(manager: CLLocationManager!, didFailWithError error: NSError!) {
        println("Error while updating location " + error.localizedDescription)
    }
    
    func postLocation(params : Dictionary<String, AnyObject>, postCompleted : (succeeded: Bool, msg: String) -> ()) {
        var request = NSMutableURLRequest(URL: NSURL(string: "http://whatdoido.csse.rose-hulman.edu/api/location/add")!)
        var session = NSURLSession.sharedSession()
        request.HTTPMethod = "POST"
        
        var err: NSError?
        request.HTTPBody = NSJSONSerialization.dataWithJSONObject(params, options: nil, error: &err)
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        request.addValue("application/json", forHTTPHeaderField: "Accept")
        
        var task = session.dataTaskWithRequest(request) {data, response, error -> Void in
            println("Response: \(response)")
            var strData = NSString(data: data, encoding: NSUTF8StringEncoding)
            println("Body: \(strData)")
            var err: NSError?
            var json = NSJSONSerialization.JSONObjectWithData(data, options: .MutableLeaves, error: &err) as? NSDictionary
            
            var msg = "No message"
            
            // Did the JSONObjectWithData constructor return an error? If so, log the error to the console
            if(err != nil) {
                println(err!.localizedDescription)
                let jsonStr = NSString(data: data, encoding: NSUTF8StringEncoding)
                println("Error could not parse JSON: '\(jsonStr)'")
                postCompleted(succeeded: false, msg: "Error")
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
                        postCompleted(succeeded: success, msg: "Posted location")
                    }
                    return
                }
                else {
                    // Woa, okay the json object was nil, something went worng. Maybe the server isn't running?
                    let jsonStr = NSString(data: data, encoding: NSUTF8StringEncoding)
                    println("Error could not parse JSON: \(jsonStr)")
                    postCompleted(succeeded: false, msg: "Error")
                }
            }
        }
        
        task.resume()
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    

    func load(name: String) {
        loadedName = name
    }

    func refreshUI() {
        //let delText = del.user.getName()
        //if (delText == "Unknown User") {
        //    uNameLabel.text = loadedName
        //} else {
        uNameLabel.text = "Hello, " + del.user.getName()
        suggestionTableView.reloadData()
        //}
    }
    
    override func prepareForSegue(segue: UIStoryboardSegue, sender: AnyObject!) {
        if (segue.identifier == "suggestionSegue") {
            var vc = segue.destinationViewController as SuggestionViewController
            vc.pageState = 0
            vc.originView = 0
        }
    }

}
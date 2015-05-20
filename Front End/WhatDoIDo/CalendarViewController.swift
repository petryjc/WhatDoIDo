//
//  CalendarViewController.swift
//  WhatDoIDo
//
//  Created by CSSE Department on 1/27/15.
//  Copyright (c) 2015 PaJamaKinG. All rights reserved.
//

import Foundation
import UIKit

class CalendarViewController: UIViewController, CVCalendarViewDelegate {
    @IBOutlet weak var calendarView: CVCalendarView!
    @IBOutlet weak var menuView: CVCalendarMenuView!
    @IBOutlet weak var monthLabel: UILabel!
    var shouldShowDaysOut = false
    var animationFinished = true
    var monthSuggestions = [[SuggestionModel]]()
    var selectedDay: CVDate?
    var del = UIApplication.sharedApplication().delegate as AppDelegate
    
    override func viewDidAppear(animated: Bool) {
        super.viewDidAppear(animated)
        
        self.calendarView.commitCalendarViewUpdate()
        self.menuView.commitMenuViewUpdate()
        
        self.calendarView.delegate = self
        
        pullMonth(["token": del.user.getLoginToken(),
                   "beginning": "\(self.calendarView.presentedDate!.month!)-01-\(self.calendarView.presentedDate!.year!)",
                   "ending": getNextMonth(self.calendarView.presentedDate!)]) { (succeeded: Bool, msg: String) -> () in
            println(succeeded, msg)
            // Move to the UI thread
            dispatch_async(dispatch_get_main_queue(), { () -> Void in
            })
        }
    }
    
    
    
    
    func shouldShowWeekdaysOut() -> Bool {
        return self.shouldShowDaysOut
    }
    
    func didSelectDayView(dayView: CVCalendarDayView) {
        //println(dayView.date);
        //println(self.monthSuggestions[dayView.date!.day! - 1])
        self.selectedDay = dayView.date!
        performSegueWithIdentifier("dayDetailSegue", sender: self);
    }
    
    func dotMarker(colorOnDayView dayView: CVCalendarDayView) -> UIColor {
        /*var numSuggestions = self.monthSuggestions[dayView.date!.day! - 1].count
        if numSuggestions <= 3 {
            return .greenColor()
        } else if numSuggestions <= 5 {
            return .blueColor()
        } else if numSuggestions >= 9 {
            return .redColor()
        }*/
        
        return .whiteColor()
    }
    
    func dotMarker(shouldShowOnDayView dayView: CVCalendarDayView) -> Bool {
        return false // self.monthSuggestions[dayView.date!.day! - 1].count != 0
    }
    
    func dotMarker(shouldMoveOnHighlightingOnDayView dayView: CVCalendarDayView) -> Bool {
        return false
    }
    
    func topMarker(shouldDisplayOnDayView dayView: CVCalendarDayView) -> Bool {
        return true
    }
    
    func getNextMonth(date: CVDate) -> String {
        if (date.month < 12) {
            return "\(date.month!+1)-01-\(date.year!)"
        } else {
            return "01-01-\(date.year!+1)"
        }
    }
    
    func presentedDateUpdated(date: CVDate) {
        if self.monthLabel.text != date.description() && self.animationFinished {
            let updatedMonthLabel = UILabel()
            updatedMonthLabel.textColor = monthLabel.textColor
            updatedMonthLabel.font = monthLabel.font
            updatedMonthLabel.textAlignment = .Center
            updatedMonthLabel.text = date.description
            updatedMonthLabel.sizeToFit()
            updatedMonthLabel.alpha = 0
            updatedMonthLabel.center = self.monthLabel.center
            
            pullMonth(["token": del.user.getLoginToken(), "beginning": "\(date.month!)-01-\(date.year!)", "ending": getNextMonth(date)]) { (succeeded: Bool, msg: String) -> () in
                println(succeeded, msg)
                // Move to the UI thread
                dispatch_async(dispatch_get_main_queue(), { () -> Void in
                })
            }
            
            let offset = CGFloat(48)
            updatedMonthLabel.transform = CGAffineTransformMakeTranslation(0, offset)
            updatedMonthLabel.transform = CGAffineTransformMakeScale(1, 0.1)
            
            UIView.animateWithDuration(0.35, delay: 0, options: UIViewAnimationOptions.CurveEaseIn, animations: { () -> Void in
                self.animationFinished = false
                self.monthLabel.transform = CGAffineTransformMakeTranslation(0, -offset)
                self.monthLabel.transform = CGAffineTransformMakeScale(1, 0.1)
                self.monthLabel.alpha = 0
                
                updatedMonthLabel.alpha = 1
                updatedMonthLabel.transform = CGAffineTransformIdentity
                
                }) { (finished) -> Void in
                    self.animationFinished = true
                    self.monthLabel.frame = updatedMonthLabel.frame
                    self.monthLabel.text = updatedMonthLabel.text
                    self.monthLabel.transform = CGAffineTransformIdentity
                    self.monthLabel.alpha = 1
                    updatedMonthLabel.removeFromSuperview()
            }
            
            self.view.insertSubview(updatedMonthLabel, aboveSubview: self.monthLabel)
        }
    }
    
    
    
    
    func pullMonth(params : Dictionary<String, AnyObject>, postCompleted : (succeeded: Bool, msg: String) -> ()) {
        var request = NSMutableURLRequest(URL: NSURL(string: "http://whatdoido.csse.rose-hulman.edu/api/suggestion/calendar")!)
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
                        var code = status["code"] as Int
                        var success = code == 0
                        //self.monthSuggestions = convertJsonArrayToSuggestionArray(parseJSON["calendar"])
                        self.convertJsonArrayToSuggestionArray(parseJSON)
                        postCompleted(succeeded: success, msg: "Pulled suggestions")
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
    
    func convertJsonArrayToSuggestionArray(json: NSDictionary) {
        println("Convert JSON Array to Suggestion Array.")
        var events = json["calendar"]!
        if (events.count < 1) {
            println("There were no events")
            self.monthSuggestions = [[SuggestionModel]]();
            for (var j = 0; j < 32; j++) {
                self.monthSuggestions.append([SuggestionModel]())
            }
        } else {
            self.monthSuggestions = [[SuggestionModel]]();
            for (var j = 0; j < 32; j++) {
                self.monthSuggestions.append([SuggestionModel]())
            }
            //println(self.monthSuggestions)
            for (var i = 0; i < events.count; i++) {
                var event = events[i]!
                var sug = SuggestionModel()
                //sug.name = NSString(data: event["name"]!, encoding: NSUTF8StringEncoding)
                //sug.name = event["name"] as String
                sug.setName(event["name"] as String)
                //println(event["name"] as String)
                sug.location = event["location"] as String
                var beginningDate = split(event["beginning"] as String) {$0 == "-"}
                var after2ndDash = split(beginningDate[2]) {$0 == "T"}
                sug.startTime = event["beginning"] as String
                sug.endTime = event["ending"] as String
                var mon = (self.monthSuggestions[after2ndDash[0].toInt()! - 1])
                mon.append(sug)
                self.monthSuggestions[after2ndDash[0].toInt()! - 1] = mon
            }
            //println(self.monthSuggestions)
        }
    }
    
    //I'm Peter and I suck lol
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        // Do any additional setup after loading the view, typically from a nib.
        refreshUI();
    }
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    func refreshUI() {
        self.monthLabel.text = CVDate(date: NSDate()).description()
    }
    
    override func prepareForSegue(segue: UIStoryboardSegue, sender: AnyObject!) {
        if (segue.identifier == "dayDetailSegue") {
            var vc = segue.destinationViewController as DayDetailViewController
            vc.suggestionList = self.monthSuggestions[self.selectedDay!.day! - 1]
            vc.date = self.selectedDay
        }
    }
}
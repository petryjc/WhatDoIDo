//
//  UserModel.swift
//  WhatDoIDo
//
//  Created by CSSE Department on 10/2/14.
//  Copyright (c) 2014 PaJamaKinG. All rights reserved.
//

import Foundation

class UserModel {
    
    var name: String
    var password: String
    var loginSuccess: Bool
    var loginToken: String
    var suggestionList: [SuggestionModel]
    
    init() {
        name = "Unknown User"
        password = ""
        loginSuccess = false
        loginToken = ""
        suggestionList = []
    }
    
    func getName() -> String {
        return self.name
    }
    
    func changeName(name: String) {
        if (!name.isEmpty) {
            self.name = name
        }
    }
    
    func getPass() -> String {
        return self.password
    }
    
    func changePassword(pass: String) {
        if (!pass.isEmpty) {
            self.password = pass
        }
    }
    
    func getLoginToken() -> String {
        return self.loginToken
    }
    
    func setLoginToken(token: String) {
        self.loginToken = token
    }
    
    func wasLoginSuccessful() -> Bool {
        return self.loginSuccess
    }
    
    func postFailure() {
        self.loginSuccess = false
    }
    
    func postSuccess() {
        self.loginSuccess = true
    }
    
    func convertJsonArrayToSuggestionArray(json: NSDictionary) -> [SuggestionModel] {
        println("Convert JSON Array to Suggestion Array.")
        var events = json["calendar"]!
        var suggestions = [SuggestionModel]();
        //println(self.monthSuggestions)
        for (var i = 0; i < events.count; i++) {
            var event = events[i]!
            var sug = SuggestionModel()
            //sug.name = NSString(data: event["name"]!, encoding: NSUTF8StringEncoding)
            //sug.name = event["name"] as String
            println(event["name"] as String)
            sug.setName(event["name"] as String)
            //println(event["name"] as String)
            sug.location = event["location"] as String
            sug.startTime = event["beginning"] as String
            sug.endTime = event["ending"] as String
            suggestions.append(sug)
        }
        println(suggestions)
        return suggestions
    }
    
    func login(params : Dictionary<String, String>, url : String, postCompleted : (succeeded: Bool, msg: String, token: String) -> ()) {
        var request = NSMutableURLRequest(URL: NSURL(string: url)!)
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
                postCompleted(succeeded: false, msg: "Something went wrong, try again", token: "")
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
                            postCompleted(succeeded: success, msg: "Logged in.", token: parseJSON["token"] as String)
                        } else {
                            postCompleted(succeeded: success, msg: status["msg"] as String, token: "")
                        }
                    }
                    return
                }
                else {
                    // Woa, okay the json object was nil, something went worng. Maybe the server isn't running?
                    let jsonStr = NSString(data: data, encoding: NSUTF8StringEncoding)
                    println("Error could not parse JSON: \(jsonStr)")
                    postCompleted(succeeded: false, msg: "The server appears to be down", token: "")
                }
            }
        }
        
        task.resume()
    }
    
    func logout(params : Dictionary<String, String>, url : String, postCompleted : (succeeded: Bool, msg: String) -> ()) {
        var request = NSMutableURLRequest(URL: NSURL(string: url)!)
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
                        postCompleted(succeeded: success, msg: "Logged in.")
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
    
    func register(params : Dictionary<String, String>, url : String, postCompleted : (succeeded: Bool, msg: String) -> ()) {
        var request = NSMutableURLRequest(URL: NSURL(string: url)!)
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
                        postCompleted(succeeded: success, msg: "Logged in.")
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
    
    func deleteAccount(params : Dictionary<String, String>, url : String, postCompleted : (succeeded: Bool, msg: String) -> ()) {
        var request = NSMutableURLRequest(URL: NSURL(string: url)!)
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
                        postCompleted(succeeded: success, msg: "Logged in.")
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
    
    func todaysSuggestions(postCompleted : (succeeded: Bool, msg: String, suggestions: [SuggestionModel]?) -> ()) {
        var request = NSMutableURLRequest(URL: NSURL(string: "http://whatdoido.csse.rose-hulman.edu/api/suggestion/calendar")!)
        var session = NSURLSession.sharedSession()
        request.HTTPMethod = "POST"
        
        var todaysDate:NSDate = NSDate()
        var dateFormatter:NSDateFormatter = NSDateFormatter()
        dateFormatter.dateFormat = "MM-dd-yyyy"
        var dateInFormat:String = dateFormatter.stringFromDate(todaysDate)
        
        var err: NSError?
        request.HTTPBody = NSJSONSerialization.dataWithJSONObject(["token": self.getLoginToken(), "beginning": dateInFormat, "ending": dateInFormat], options: nil, error: &err)
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        request.addValue("application/json", forHTTPHeaderField: "Accept")
        
        var task = session.dataTaskWithRequest(request) {data, response, error -> Void in
            var strData = NSString(data: data, encoding: NSUTF8StringEncoding)
            println("Body: \(strData)")
            var err: NSError?
            var json = NSJSONSerialization.JSONObjectWithData(data, options: .MutableLeaves, error: &err) as? NSDictionary
            
            var msg = "No message"
            // Did the JSONObjectWithData constructor return an error? If so, log the error to the console
            if(err != nil) {
                println(err!.localizedDescription)
                let jsonStr = NSString(data: data, encoding: NSUTF8StringEncoding)
                postCompleted(succeeded: false, msg: "Error", suggestions: [SuggestionModel]())
            } else {
                // The JSONObjectWithData constructor didn't return an error. But, we should still
                // check and make sure that json has a value using optional binding.
                if let parseJSON = json {
                    println(parseJSON)
                    // Okay, the parsedJSON is here, let's get the value for 'status' out of it
                    if let status = parseJSON["status"] as? NSDictionary {
                        var code = status["code"] as Int
                        var success = code == 0
                        //self.monthSuggestions = convertJsonArrayToSuggestionArray(parseJSON["calendar"])
                        var suggestionList = self.convertJsonArrayToSuggestionArray(parseJSON)
                        self.suggestionList = suggestionList
                        postCompleted(succeeded: success, msg: "Pulled suggestions", suggestions: suggestionList)
                    }
                    return
                }
                else {
                    // Woa, okay the json object was nil, something went worng. Maybe the server isn't running?
                    let jsonStr = NSString(data: data, encoding: NSUTF8StringEncoding)
                    println("Error could not parse JSON: \(jsonStr)")
                    postCompleted(succeeded: false, msg: "Error", suggestions: [SuggestionModel]())
                }
            }
        }
        
        task.resume()
    }
    
    func suggest(params : Dictionary<String, String>, postCompleted : (succeeded: Bool, msg: String, json: NSDictionary?) -> ()) {
        var request = NSMutableURLRequest(URL: NSURL(string: "http://whatdoido.csse.rose-hulman.edu/api/suggestion/single")!)
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
                postCompleted(succeeded: false, msg: "Error", json: nil)
            }
            else {
                // The JSONObjectWithData constructor didn't return an error. But, we should still
                // check and make sure that json has a value using optional binding.
                if let parseJSON = json {
                    println(parseJSON)
                    var cost = parseJSON["cost"] as Int
                    var success = cost == 11
                    if (success) {
                        postCompleted(succeeded: success, msg: "Got the suggestion", json: parseJSON)
                    } else {
                        postCompleted(succeeded: success, msg: "Failed to get the suggestion", json: parseJSON)
                    }
                    return
                }
                else {
                    // Woa, okay the json object was nil, something went worng. Maybe the server isn't running?
                    let jsonStr = NSString(data: data, encoding: NSUTF8StringEncoding)
                    println("Error could not parse JSON: \(jsonStr)")
                    postCompleted(succeeded: false, msg: "Error", json: nil)
                }
            }
        }
        
        task.resume()
    }
}
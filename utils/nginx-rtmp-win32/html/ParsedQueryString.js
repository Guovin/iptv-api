/*******************************************************************************
 * 
 * ParsedQueryString version 1.0
 * Copyright 2007, Jeff Mott <Mott.Jeff@gmail.com>. All rights reserved.
 * 
 * Redistribution and use in source and binary forms with or without
 * modification are permitted provided that the above copyright notice,
 * this condition, and the following disclaimer are retained.
 *
 * THIS SOFTWARE IS PROVIDED AS IS, AND ANY EXPRESS OR IMPLIED WARRANTIES,
 * INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
 * FITNESS FOR A PARTICULAR PURPOSE, ARE DISCLAIMED. IN NO EVENT SHALL THE
 * COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING BUT NOT
 * LIMITED TO PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
 * EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 * 
 ******************************************************************************/

function ParsedQueryString() {
    this._init();
}

ParsedQueryString.version = '1.0';

ParsedQueryString.prototype =
{
    _init:
        function ()
        {
            this._parameters = {};

            if (location.search.length <= 1)
                return;
            var pairs = location.search.substr(1).split(/[&;]/);
            for (var i = 0; i < pairs.length; i++)
            {
                var pair = pairs[i].split(/=/);
                var name = this._decodeURL(pair[0]);
                if (Boolean(pair[1]))
                {
                    var value = this._decodeURL(pair[1]);
                    if (Boolean(this._parameters[name]))
                        this._parameters[name].push(value);
                    else
                        this._parameters[name] = [value];
                }
            }
        },

    _decodeURL:
        function (url) {
            return decodeURIComponent(url.replace(/\+/g, " "));
        },

    param:
        function (name)
        {
            if (Boolean(this._parameters[name]))
                return this._parameters[name][0];
            else
                return "";
        },

    params:
        function (name)
        {
            if (Boolean(name))
            {
                if (Boolean(this._parameters[name]))
                {
                    var values = [];
                    for (var i = 0; i < this._parameters[name].length; i++)
                        values.push(this._parameters[name][i]);
                    return values;
                }
                else
                    return [];
            }
            else
            {
                var names = [];
                for (var name in this._parameters)
                    names.push(name);
                return names;
            }
        }
};
